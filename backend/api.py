from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date, timedelta
import io
import pandas as pd
from database import get_db
from models_db import Orders, Returns, Products, MetricsSummary, SyncHistory
from schemas import (
    DashboardResponse, StockResponse, LogisticsResponse, 
    ProductDetailResponse, SyncStatus, TooltipResponse, KpiData, ProductSummary
)
import uuid
from uuid import UUID 
from auth import get_current_user

router = APIRouter()

def get_user_id():
    return "00000000-0000-0000-0000-000000000001"
@router.get("/api/sync/status", response_model=SyncStatus)
def get_sync_status(db: Session = Depends(get_db)):
    last = db.query(SyncHistory).order_by(SyncHistory.start_time.desc()).first()
    return SyncStatus(
        message=last.status if last else "Нет синхронизаций",
        session_id=last.id if last else "none"
    )

@router.post("/api/sync/trigger")
def trigger_sync(
    user_id: str = Depends(get_current_user),  # ✅ Получаем ID из токена
    db: Session = Depends(get_db)
):
    from uuid import UUID
    from datetime import datetime
    
    user_uuid = UUID(user_id)  # ✅ Конвертация для PostgreSQL
    
    # Записываем начало синхронизации в историю
    sync_record = SyncHistory(
        user_id=user_uuid,  # ✅ Используем реальный UUID из токена
        start_time=datetime.utcnow(),
        status="in_progress",
        error_message=None
    )
    db.add(sync_record)
    db.commit()
    
    try:
        # 🔄 Здесь была бы логика реального запроса к Ozon API
        # Для MVP: имитируем успешную синхронизацию
        import time
        time.sleep(1)  # Имитация задержки
        
        # Обновляем запись об успешном завершении
        sync_record.end_time = datetime.utcnow()
        sync_record.status = "completed"
        db.commit()
        
        return {"status": "success", "message": "Синхронизация завершена"}
        
    except Exception as e:
        # При ошибке обновляем запись с информацией об ошибке
        sync_record.end_time = datetime.utcnow()
        sync_record.status = "failed"
        sync_record.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации: {str(e)}")

@router.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard(
    period: int = Query(30, ge=1, le=365),
    logistics: str = Query("both"),
    user_id: str = Depends(get_current_user),  # Приходит как строка
    db: Session = Depends(get_db)
):
    # ✅ Явно конвертируем строку из токена в UUID для PostgreSQL
    user_uuid = UUID(user_id)
    
    from datetime import date, timedelta
    from collections import defaultdict
    from sqlalchemy import func
    
    start_date = date.today() - timedelta(days=period)
    
    # 🔍 Отладка: смотрим, сколько всего заказов у этого юзера в БД
    total_in_db = db.query(Orders).filter(Orders.user_id == user_uuid).count()
    print(f"🔍 DEBUG: Всего заказов в БД для user {user_uuid}: {total_in_db}")
    
    # 1. Загружаем заказы (убрали фильтр status, чтобы точно получить данные)
    orders_query = db.query(Orders).filter(
        Orders.user_id == user_uuid,
        Orders.date >= start_date
    )
    if logistics != "both":
        orders_query = orders_query.filter(Orders.logistics_type == logistics)
    orders = orders_query.all()
    
    print(f"🔍 DEBUG: Найдено заказов за период: {len(orders)}")

    # Если данных нет — возвращаем 404
    if not orders:
        raise HTTPException(
            status_code=404,
            detail=f"Нет данных за период {period} дней. Проверьте seed.py и user_id."
        )
    
    # 2. Считаем метрики
    total_revenue = sum(o.revenue for o in orders)
    total_orders = len(orders)
    
    # Возвраты
    order_ids = [o.order_id for o in orders]
    returns = db.query(Returns).filter(
        Returns.user_id == user_uuid,
        Returns.order_id.in_(order_ids)
    ).all()
    total_returns = sum(r.quantity for r in returns)
    
    avg_check = round(float(total_revenue / total_orders), 2) if total_orders > 0 else 0.0
    return_rate = round((total_returns / total_orders * 100), 2) if total_orders > 0 else 0.0
    
    # 3. График по дням
    daily_revenue = defaultdict(float)
    for o in orders:
        daily_revenue[o.date] += float(o.revenue)
    revenue_chart = [{"date": d.isoformat(), "value": v} for d, v in sorted(daily_revenue.items())]
    
    # 4. ТОП-5 товаров
    top_query = db.query(Orders.sku, func.sum(Orders.revenue).label("rev")).filter(
        Orders.user_id == user_uuid, Orders.date >= start_date
    ).group_by(Orders.sku).order_by(func.sum(Orders.revenue).desc()).limit(5)
    
    top_products = []
    for sku, rev in top_query.all():
        prod = db.query(Products).filter(Products.sku == sku, Products.user_id == user_uuid).first()
        if prod:
            top_products.append({"sku": prod.sku, "name": prod.name, "revenue": float(rev), "stock": prod.stock, "logistics": prod.logistics_type})
            
    return {
        "kpi": {"revenue": float(total_revenue), "orders": total_orders, "avg_check": avg_check, "return_rate": return_rate},
        "revenue_chart": revenue_chart,
        "top_products": top_products
    }

@router.get("/api/stock", response_model=StockResponse)
def get_stock(
    period: int = Query(30),  # period не используется для остатков, но оставляем для совместимости
    logistics: str = Query("both"),
    user_id: str = Depends(get_current_user),  # ✅ Получаем ID из токена
    db: Session = Depends(get_db)
):
    from uuid import UUID
    user_uuid = UUID(user_id)  # ✅ Конвертируем строку в UUID для PostgreSQL
    
    # Запрос к таблице Products
    prods = db.query(Products).filter(Products.user_id == user_uuid)
    if logistics != "both":
        prods = prods.filter(Products.logistics_type == logistics)
    prods = prods.all()
    
    # ✅ Порог низкого остатка: < 10 штук
    LOW_STOCK_THRESHOLD = 10
    
    total_val = sum(p.stock * 500 for p in prods)  # 500 — средняя цена для оценки
    low = [p for p in prods if p.stock < LOW_STOCK_THRESHOLD]
    out = [p for p in prods if p.stock == 0]
    
    return StockResponse(
        total_products=len(prods),
        total_stock_value=float(total_val),
        low_stock_count=len(low),
        out_of_stock_count=len(out),
        stock_by_warehouse=[
            {"name": "Склад FBO", "stock": sum(p.stock for p in prods if p.logistics_type == "FBO")},
            {"name": "Склад FBS", "stock": sum(p.stock for p in prods if p.logistics_type == "FBS")}
        ],
        low_stock_products=[
            {"sku": p.sku, "name": p.name, "stock": p.stock, "threshold": LOW_STOCK_THRESHOLD} 
            for p in low
        ]
    )

@router.get("/api/logistics", response_model=LogisticsResponse)
def get_logistics(
    period: int = Query(30),
    logistics: str = Query("both"),
    user_id: str = Depends(get_current_user),  # ✅ Получаем ID из токена
    db: Session = Depends(get_db)
):
    from uuid import UUID
    user_uuid = UUID(user_id)  # ✅ Конвертируем строку в UUID
    
    start = date.today() - timedelta(days=period)
    orders = db.query(Orders).filter(Orders.user_id == user_uuid, Orders.date >= start)
    if logistics != "both":
        orders = orders.filter(Orders.logistics_type == logistics)
        
    all_orders = orders.all()
    fbo = [o for o in all_orders if o.logistics_type == "FBO"]
    fbs = [o for o in all_orders if o.logistics_type == "FBS"]
    
    # ✅ РЕАЛЬНЫЕ РАСХОДЫ: FBO ~150₽ за заказ, FBS ~220₽ за заказ
    fbo_cost = len(fbo) * 150
    fbs_cost = len(fbs) * 220
    
    chart = []
    for i in range(min(period, 7)):
        d = date.today() - timedelta(days=i)
        chart.append({
            "date": d.strftime("%d.%m"),
            "fbo": len([o for o in fbo if o.date == d]),
            "fbs": len([o for o in fbs if o.date == d])
        })
    chart.reverse()
        
    return LogisticsResponse(
        total_orders_fbo=len(fbo),
        total_orders_fbs=len(fbs),
        avg_delivery_time_fbo=2.8,
        avg_delivery_time_fbs=4.1,
        total_logistics_cost=fbo_cost + fbs_cost,
        logistics_cost_fbo=fbo_cost,
        logistics_cost_fbs=fbs_cost,
        delivery_chart=chart,
        cost_by_type=[{"type": "FBO", "cost": fbo_cost}, {"type": "FBS", "cost": fbs_cost}]
    )

@router.get("/api/product/{sku}", response_model=ProductDetailResponse)
def get_product(
    sku: str,
    period: int = Query(30),
    user_id: str = Depends(get_current_user),  # ✅ Получаем ID из токена
    db: Session = Depends(get_db)
):
    from uuid import UUID
    user_uuid = UUID(user_id)  # ✅ Конвертация для PostgreSQL
    
    start = date.today() - timedelta(days=period)
    
    # Ищем товар с учётом владельца
    prod = db.query(Products).filter(
        Products.sku == sku, 
        Products.user_id == user_uuid
    ).first()
    
    if not prod:
        raise HTTPException(status_code=404, detail="Товар не найден")
        
    orders = db.query(Orders).filter(
        Orders.sku == sku, 
        Orders.user_id == user_uuid, 
        Orders.date >= start
    ).all()
    
    revenue = sum(o.revenue for o in orders)
    qty = sum(o.quantity for o in orders)
    
    chart = []
    for i in range(min(period, 14)):
        d = date.today() - timedelta(days=i)
        day_rev = sum(o.revenue for o in orders if o.date == d)
        chart.append({"date": d.isoformat(), "value": float(day_rev)})
        
    return ProductDetailResponse(
        sku=prod.sku, 
        name=prod.name, 
        revenue=float(revenue),
        quantity_sold=qty, 
        stock=prod.stock, 
        sales_chart=chart
    )

@router.get("/api/export")
def export_report(
    scope: str = Query(...),
    format: str = Query("xlsx"),
    period: int = Query(30),
    logistics: str = Query("both"),
    sku: str = Query(None),
    user_id: str = Depends(get_current_user),  # ✅ Защита токеном
    db: Session = Depends(get_db)
):
    from uuid import UUID
    user_uuid = UUID(user_id)  # ✅ Конвертация для PostgreSQL
    
    import pandas as pd
    import io
    from fastapi.responses import StreamingResponse
    from fastapi import HTTPException
    
    start = date.today() - timedelta(days=period)
    data = []
    filename = "report.xlsx"
    
    if scope == "dashboard":
        # ✅ Запрашиваем заказы напрямую (так как metrics_summary пуст)
        orders_q = db.query(Orders).filter(
            Orders.user_id == user_uuid,
            Orders.date >= start
        )
        if logistics != "both":
            orders_q = orders_q.filter(Orders.logistics_type == logistics)
        orders = orders_q.order_by(Orders.date.asc()).all()

        if not orders:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")

        # Агрегация по дням
        from collections import defaultdict
        daily = defaultdict(lambda: {"revenue": 0.0, "count": 0})
        for o in orders:
            daily[o.date]["revenue"] += float(o.revenue)
            daily[o.date]["count"] += 1

        data = []
        total_rev, total_cnt = 0.0, 0
        for d, vals in sorted(daily.items()):
            avg = vals["revenue"] / vals["count"] if vals["count"] > 0 else 0
            data.append({
                "Дата": d.strftime("%d.%m.%Y"),
                "Выручка": round(vals["revenue"], 2),
                "Заказы": vals["count"],
                "Ср. чек": round(avg, 2)
            })
            total_rev += vals["revenue"]
            total_cnt += vals["count"]

        # Итоговая строка
        avg_total = total_rev / total_cnt if total_cnt > 0 else 0
        data.insert(0, {
            "Дата": "ИТОГО",
            "Выручка": round(total_rev, 2),
            "Заказы": total_cnt,
            "Ср. чек": round(avg_total, 2)
        })
        filename = f"dashboard_{period}_{logistics}.xlsx"

    elif scope == "stock":
        prods = db.query(Products).filter(Products.user_id == user_uuid)  # ✅
        if logistics != "both": 
            prods = prods.filter(Products.logistics_type == logistics)
        prods = prods.all()
        if not prods:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
        data = [
            {"SKU": p.sku, "Название": p.name, "Остаток": p.stock, "Логистика": p.logistics_type} for p in prods
        ]
        filename = f"stock_{period}_{logistics}.xlsx"

    elif scope == "logistics":
        orders = db.query(Orders).filter(Orders.user_id == user_uuid, Orders.date >= start)  # ✅
        if logistics != "both": 
            orders = orders.filter(Orders.logistics_type == logistics)
        orders = orders.all()
        if not orders:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
        data = [
            {
                "ID заказа": o.order_id,
                "Дата": o.date.strftime("%d.%m.%Y"),
                "Логистика": o.logistics_type,
                "Сумма": round(float(o.revenue), 2),
                "Статус": o.status
            } for o in orders
        ]
        filename = f"logistics_{period}_{logistics}.xlsx"

    elif scope == "returns":
        returns = db.query(Returns).filter(Returns.user_id == user_uuid, Returns.date >= start).all()  # ✅
        if not returns:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
        data = [
            {
                "ID заказа": r.order_id,
                "SKU": r.sku,
                "Дата": r.date.strftime("%d.%m.%Y"),
                "Количество": r.quantity,
                "Сумма возврата": round(float(r.amount), 2),
                "Причина": r.reason or "Не указана"
            } for r in returns
        ]
        filename = f"returns_{period}_{logistics}.xlsx"

    elif scope == "product" and sku:
        orders = db.query(Orders).filter(Orders.sku == sku, Orders.user_id == user_uuid, Orders.date >= start)  # ✅
        if logistics != "both": 
            orders = orders.filter(Orders.logistics_type == logistics)
        orders = orders.all()
        if not orders:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
            
        prod = db.query(Products).filter(Products.sku == sku, Products.user_id == user_uuid).first()  # ✅
        total_rev = sum(o.revenue for o in orders)
        total_qty = sum(o.quantity for o in orders)
        
        data.append({"SKU": sku, "Название": prod.name if prod else sku, "Всего продано": total_qty, "Выручка": round(float(total_rev), 2)})
        data.extend([
            {
                "Дата": o.date.strftime("%d.%m.%Y"),
                "Кол-во": o.quantity,
                "Сумма": round(float(o.revenue), 2),
                "Статус": o.status
            } for o in orders
        ])
        filename = f"product_{sku}.xlsx"
        
    else:
        raise HTTPException(status_code=400, detail="Неверный тип отчёта или отсутствуют параметры")

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Отчёт')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/api/returns")
def get_returns(
    period: int = Query(30),
    logistics: str = Query("both"),
    user_id: str = Depends(get_current_user),  # ✅ Получаем ID из токена
    db: Session = Depends(get_db)
):
    from uuid import UUID
    user_uuid = UUID(user_id)  # ✅ Конвертируем строку в UUID для PostgreSQL

    start = date.today() - timedelta(days=period)
    
    # 1. Загружаем ВСЕ возвраты за период
    returns = db.query(Returns).filter(
        Returns.user_id == user_uuid,  # ✅ Используем UUID
        Returns.date >= start
    ).all()
    
    # 2. Загружаем заказы для расчёта доли возвратов
    orders = db.query(Orders).filter(
        Orders.user_id == user_uuid,   # ✅ Используем UUID
        Orders.date >= start
    ).all()
    
    # 3. Считаем метрики на уровне Python
    total_returns_count = sum(r.quantity for r in returns)
    total_return_amount = sum(r.amount for r in returns)
    orders_count = len(orders)
    return_rate = round((total_returns_count / orders_count * 100), 2) if orders_count > 0 else 0.0

    # 4. График возвратов по дням
    chart_data = []
    for i in range(period):
        d = date.today() - timedelta(days=i)
        day_ret = sum(r.quantity for r in returns if r.date == d)
        chart_data.append({"date": d.strftime("%d.%m"), "value": day_ret})
    chart_data.reverse()

    # 5. ТОП-5 возвращаемых товаров
    from collections import Counter
    sku_counter = Counter()
    sku_reasons = {}
    
    for r in returns:
        sku_counter[r.sku] += r.quantity
        if r.sku not in sku_reasons and r.reason:
            sku_reasons[r.sku] = r.reason
    
    top_5_skus = sku_counter.most_common(5)
    
    top_list = []
    for sku, qty in top_5_skus:
        # ✅ Фильтруем товары по user_uuid
        prod = db.query(Products).filter(Products.sku == sku, Products.user_id == user_uuid).first()
        reason = sku_reasons.get(sku) or "Не указана"
        top_list.append({
            "sku": sku,
            "name": prod.name if prod else sku,
            "returns": qty,
            "reason": reason
        })

    return {
        "total_returns": total_returns_count,
        "total_return_amount": float(total_return_amount),
        "return_rate": return_rate,
        "returns_chart": chart_data,
        "top_returned_products": top_list
    }

@router.get("/api/metric-tooltip", response_model=TooltipResponse)
def get_tooltip(metric_key: str):
    tooltips = {
        "revenue": {"label": "Выручка", "description": "Общая сумма продаж за период"},
        "orders": {"label": "Заказы", "description": "Количество оформленных заказов"},
        "avg_check": {"label": "Средний чек", "description": "Средняя сумма одного заказа"},
        "return_rate": {"label": "Доля возвратов", "description": "Процент возвращённых товаров"}
    }
    return tooltips.get(metric_key, {"label": metric_key, "description": "Нет описания"})
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

@router.post("/api/sync/trigger", response_model=SyncStatus)
def trigger_sync(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    db.add(SyncHistory(user_id=get_user_id(), start_time=date.today(), status="in_progress"))
    db.commit()
    return SyncStatus(message="Синхронизация запущена", session_id=session_id)

@router.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard(
    period: int = Query(30, ge=1, le=365),
    logistics: str = Query("both"),
    db: Session = Depends(get_db)
):
    start_date = date.today() - timedelta(days=period)
    query = db.query(MetricsSummary).filter(
        MetricsSummary.user_id == get_user_id(),
        MetricsSummary.date >= start_date,
        MetricsSummary.logistics_type == logistics
    )
    
    metrics = query.all()
    if not metrics:
        raise HTTPException(status_code=404, detail="Нет данных за выбранный период")
        
    total_rev = sum(m.revenue for m in metrics)
    total_ord = sum(m.orders_count for m in metrics)
    total_ret = sum(m.returns_count for m in metrics)
    
    avg_check = round(total_rev / total_ord, 2) if total_ord > 0 else 0.0
    ret_rate = round((total_ret / total_ord * 100), 2) if total_ord > 0 else 0.0
    
    chart_data = [{"date": m.date.isoformat(), "value": float(m.revenue)} for m in metrics]
    
    products = db.query(
        Orders.sku, func.sum(Orders.revenue).label("revenue")
    ).filter(
        Orders.user_id == get_user_id(),
        Orders.date >= start_date,
        (Orders.logistics_type == logistics if logistics != "both" else True)
    ).group_by(Orders.sku).order_by(func.sum(Orders.revenue).desc()).limit(5).all()
    
    top_list = []
    for sku, rev in products:
        prod = db.query(Products).filter(Products.sku == sku).first()
        if prod:
            top_list.append(ProductSummary(
                sku=prod.sku, 
                name=prod.name, 
                revenue=float(rev), 
                stock=prod.stock, 
                logistics=prod.logistics_type
            ))
            
    return DashboardResponse(
        kpi=KpiData(
            revenue=float(total_rev), 
            orders=total_ord, 
            avg_check=avg_check, 
            return_rate=ret_rate
        ),
        revenue_chart=chart_data,
        top_products=top_list
    )

@router.get("/api/stock", response_model=StockResponse)
def get_stock(
    period: int = Query(30),
    logistics: str = Query("both"),
    db: Session = Depends(get_db)
):
    prods = db.query(Products).filter(Products.user_id == get_user_id())
    if logistics != "both":
        prods = prods.filter(Products.logistics_type == logistics)
    prods = prods.all()
    
    # ✅ Порог низкого остатка: < 10 штук
    LOW_STOCK_THRESHOLD = 10
    
    total_val = sum(p.stock * 500 for p in prods)
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
    db: Session = Depends(get_db)
):
    start = date.today() - timedelta(days=period)
    orders = db.query(Orders).filter(Orders.user_id == get_user_id(), Orders.date >= start)
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
def get_product(sku: str, period: int = Query(30), db: Session = Depends(get_db)):
    prod = db.query(Products).filter(Products.sku == sku, Products.user_id == get_user_id()).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Товар не найден")
        
    start = date.today() - timedelta(days=period)
    orders = db.query(Orders).filter(Orders.sku == sku, Orders.user_id == get_user_id(), Orders.date >= start).all()
    
    revenue = sum(o.revenue for o in orders)
    qty = sum(o.quantity for o in orders)
    
    chart = []
    for i in range(min(period, 14)):
        d = date.today() - timedelta(days=i)
        day_rev = sum(o.revenue for o in orders if o.date == d)
        chart.append({"date": d.isoformat(), "value": float(day_rev)})
        
    return ProductDetailResponse(
        sku=prod.sku, name=prod.name, revenue=float(revenue),
        quantity_sold=qty, stock=prod.stock, sales_chart=chart
    )

@router.get("/api/export")
def export_report(
    scope: str, format: str, period: int, logistics: str, sku: str = None, db: Session = Depends(get_db)
):
    start = date.today() - timedelta(days=period)
    data = []
    filename = "report.xlsx"
    
    if scope == "dashboard":
        metrics = db.query(MetricsSummary).filter(
            MetricsSummary.user_id == get_user_id(),
            MetricsSummary.date >= start,
            MetricsSummary.logistics_type == logistics
        ).order_by(MetricsSummary.date.asc()).all()
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
            
        total_rev = sum(m.revenue for m in metrics)
        total_ord = sum(m.orders_count for m in metrics)
        avg_check = round(total_rev / total_ord, 2) if total_ord > 0 else 0.0
        ret_rate = round((sum(m.returns_count for m in metrics) / total_ord * 100), 2) if total_ord > 0 else 0.0
        
        # Сводная строка
        data.append({"Дата": "ИТОГО", "Выручка": round(float(total_rev), 2), "Заказы": total_ord, "Ср. чек": avg_check, "Доля возвратов (%)": ret_rate})
        # Ежедневные строки
        data.extend([
            {
                "Дата": m.date.strftime("%d.%m.%Y"),
                "Выручка": round(float(m.revenue), 2),
                "Заказы": m.orders_count,
                "Ср. чек": round(float(m.avg_check), 2),
                "Доля возвратов (%)": round(float(m.return_rate), 2)
            } for m in metrics
        ])
        filename = f"dashboard_{period}_{logistics}.xlsx"

    elif scope == "stock":
        prods = db.query(Products).filter(Products.user_id == get_user_id())
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
        orders = db.query(Orders).filter(Orders.user_id == get_user_id(), Orders.date >= start)
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
        returns = db.query(Returns).filter(Returns.user_id == get_user_id(), Returns.date >= start).all()
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
        orders = db.query(Orders).filter(Orders.sku == sku, Orders.user_id == get_user_id(), Orders.date >= start)
        if logistics != "both": 
            orders = orders.filter(Orders.logistics_type == logistics)
        orders = orders.all()
        if not orders:
            raise HTTPException(status_code=404, detail="Нет данных для экспорта")
            
        prod = db.query(Products).filter(Products.sku == sku, Products.user_id == get_user_id()).first()
        total_rev = sum(o.revenue for o in orders)
        total_qty = sum(o.quantity for o in orders)
        
        # Сводная по товару
        data.append({"SKU": sku, "Название": prod.name if prod else sku, "Всего продано": total_qty, "Выручка": round(float(total_rev), 2)})
        # Детализация по заказам
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
    db: Session = Depends(get_db)
):
    start = date.today() - timedelta(days=period)
    
    # 1. Загружаем ВСЕ возвраты за период в память
    returns = db.query(Returns).filter(
        Returns.user_id == get_user_id(),
        Returns.date >= start
    ).all()
    
    # 2. Загружаем заказы для расчёта доли возвратов
    orders = db.query(Orders).filter(
        Orders.user_id == get_user_id(),
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

    # 5. ТОП-5 возвращаемых товаров — БЕЗ func.first(), БЕЗ GROUP BY с агрегатами
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
        prod = db.query(Products).filter(Products.sku == sku, Products.user_id == get_user_id()).first()
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
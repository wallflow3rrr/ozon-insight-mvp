from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from openpyxl import Workbook
from auth import mock_auth 
from models import (
    SyncTriggerRequest, GetDashboardRequest, GetProductRequest,
    ExportRequest, GetMetricTooltipRequest,
    SyncStatus, DashboardResponse, ProductDetailResponse, ExportResponse
)
from mock_data import db

router = APIRouter()

@router.get("/auth/ozon/login", status_code=302)
def initiate_ozon_login():
    return {"message": "OAuth flow initiated (mock)"}

@router.get("/api/sync/status", response_model=SyncStatus)
def get_last_sync_status(user_id: str = Depends(mock_auth)):
    status_info = db.get_sync_status(user_id)
    return SyncStatus(**status_info)

@router.post("/api/sync/trigger", response_model=SyncStatus)
def trigger_sync(user_id: str = Depends(mock_auth)):
    db.generate_mock_data(user_id)
    return SyncStatus(message="Sync started", session_id="mock_session_123")

@router.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard_data(
    period: int = 30,
    logistics: str = "both",
    user_id: str = Depends(mock_auth)
):
    data = db.get_dashboard_data(user_id, period, logistics)
    if not data:
        raise HTTPException(status_code=404, detail="No dashboard data found")
    return DashboardResponse(**data)

@router.get("/api/product/{sku}", response_model=ProductDetailResponse)
def get_product_analytics(
    sku: str,
    period: int = 30,
    user_id: str = Depends(mock_auth)
):
    data = db.get_product_detail(user_id, sku)
    if not data:
        raise HTTPException(status_code=404, detail="Product not found")
    return data

@router.get("/api/export")
def export_report(
    scope: str,
    format: str,
    period: int,
    logistics: str,
    sku: str = None,
    user_id: str = Depends(mock_auth)
):
    # ✅ Проверим, что sku передан, если scope === "product"
    if scope == "product" and not sku:
        raise HTTPException(status_code=400, detail="Invalid export scope or missing SKU")

    # --- Генерация данных для экспорта ---
    if scope == "dashboard":
        data = db.get_dashboard_data(user_id, period, logistics)
        print(f"DEBUG: Dashboard data fetched: {data}")  # ✅ Отладка
        if not data:
            print("DEBUG: Dashboard data is None or empty, raising 404")  # ✅ Отладка
            raise HTTPException(status_code=404, detail="No dashboard data found")
        # ✅ Исправленный доступ к данным:
        export_data = [
            {"metric": "revenue", "value": data["kpi"]["revenue"]},
            {"metric": "orders", "value": data["kpi"]["orders"]},
            {"metric": "avg_check", "value": data["kpi"]["avg_check"]},
            {"metric": "return_rate", "value": data["kpi"]["return_rate"]},
        ]
        filename = f"dashboard_{period}_{logistics}.xlsx"
    elif scope == "top_products":
        data = db.get_dashboard_data(user_id, period, logistics)
        print(f"DEBUG: Top products data fetched: {data}")  # ✅ Отладка
        if not data:
            print("DEBUG: Top products data is None or empty, raising 404")  # ✅ Отладка
            raise HTTPException(status_code=404, detail="No dashboard data found")
        # ✅ Исправленный доступ к данным:
        export_data = [
            {"SKU": p["sku"], "Name": p["name"], "Revenue": p["revenue"], "Stock": p["stock"], "Logistics": p["logistics"]}
            for p in data["top_products"]
        ]
        filename = f"top_products_{period}_{logistics}.xlsx"
    elif scope == "product" and sku:
        detail = db.get_product_detail(user_id, sku)
        print(f"DEBUG: Product detail fetched: {detail}")  # ✅ Отладка
        if not detail:
            raise HTTPException(status_code=404, detail="Product not found")
        # ✅ Если detail — Pydantic-модель, можно оставить как есть
        export_data = [
            {"SKU": detail.sku, "Name": detail.name, "Revenue": detail.revenue, "Sold": detail.quantity_sold, "Stock": detail.stock}
        ]
        filename = f"product_{sku}.xlsx"
    elif scope == "returns":
        export_data = [
            {"Type": "Total Returns", "Value": 42},
            {"Type": "Total Return Amount", "Value": 12500},
        ]
        filename = f"returns_{period}_{logistics}.xlsx"
    elif scope == "stock":
        export_data = [
            {"Type": "Total Products", "Value": 120},
            {"Type": "Low Stock Count", "Value": 15},
        ]
        filename = f"stock_{period}_{logistics}.xlsx"
    elif scope == "logistics":
        export_data = [
            {"Type": "Total Orders FBO", "Value": 200},
            {"Type": "Total Orders FBS", "Value": 120},
        ]
        filename = f"logistics_{period}_{logistics}.xlsx"
    else:
        raise HTTPException(status_code=400, detail="Invalid export scope")

    # --- Генерация файла ---
    df = pd.DataFrame(export_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Отчёт')
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/api/metric-tooltip")
def get_metric_tooltip(metric_key: str):
    tooltips = {
        "revenue": {"label": "Выручка", "description": "Общая сумма продаж за выбранный период"},
        "return_rate": {"label": "Доля возвратов", "description": "Процент заказов, которые были возвращены"},
        "avg_check": {"label": "Средний чек", "description": "Средняя сумма одного заказа"},
    }
    tooltip = tooltips.get(metric_key)
    if not tooltip:
        raise HTTPException(status_code=404, detail="Tooltip not found")
    return tooltip

@router.get("/api/stock")
def get_stock_data(
    period: int = 30,
    logistics: str = "both",
    user_id: str = Depends(mock_auth)
):
    # Получаем ОТФИЛЬТРОВАННЫЕ данные через основной метод
    data = db.get_dashboard_data(user_id, period, logistics)
    if not data:
        raise HTTPException(status_code=404, detail="No stock data found")

    # ✅ Используем все отфильтрованные товары (уже отфильтрованы по logistics)
    # `all_filtered_products` — это список ProductSummary
    all_filtered_products = data.get("all_filtered_products", [])

    # ✅ Теперь low_stock_products — это все товары с низким остатком из отфильтрованных
    # ВАЖНО: `period` влияет на `all_filtered_products` через `get_dashboard_data`, если в нём реализована логика фильтрации остатков по периоду.
    # В текущей заглушке `stock` — это *текущий остаток*, он **не зависит от `period`**.
    # Поэтому фильтр по `period` на `low_stock_products` **не влияет**, но влияет на `logistics`.
    # Это компромисс для MVP.
    low_stock_list = [p for p in all_filtered_products if p.stock < 5]

    transformed_data = {
        "total_products": len(all_filtered_products),
        "total_stock_value": sum(p.stock for p in all_filtered_products) * 1000,
        "low_stock_count": sum(1 for p in all_filtered_products if p.stock < 5),
        "out_of_stock_count": sum(1 for p in all_filtered_products if p.stock == 0),
        "stock_by_warehouse": [
            {"name": "Склад 1", "stock": sum(p.stock for p in all_filtered_products if p.logistics == "FBO")},
            {"name": "Склад 2", "stock": sum(p.stock for p in all_filtered_products if p.logistics == "FBS")},
        ],
        # ✅ Теперь это список всех товаров с низким остатком из отфильтрованных
        "low_stock_products": low_stock_list
    }
    return transformed_data

@router.get("/api/logistics")
def get_logistics_data(
    period: int = 30,
    logistics: str = "both",
    user_id: str = Depends(mock_auth)
):
    # Получаем данные через основной метод
    data = db.get_dashboard_data(user_id, period, logistics)
    if not data:
        raise HTTPException(status_code=404, detail="No logistics data found")

    # ✅ Используем все отфильтрованные товары, а не только ТОП-5
    all_filtered_products = data.get("all_filtered_products", [])

    # Примерная логика агрегации по логистике на основе отфильтрованных товаров
    fbo_count = sum(1 for p in all_filtered_products if p.logistics == "FBO")
    fbs_count = sum(1 for p in all_filtered_products if p.logistics == "FBS")

    transformed_data = {
        "total_orders_fbo": fbo_count * 10,  # Пример
        "total_orders_fbs": fbs_count * 10,  # Пример
        "avg_delivery_time_fbo": 3.2,  # Пример
        "avg_delivery_time_fbs": 5.1,  # Пример
        "total_logistics_cost": 45000,  # Пример
        "logistics_cost_fbo": 25000,  # Пример
        "logistics_cost_fbs": 20000,  # Пример
        "delivery_chart": [  # Пример
            {"date": "2025-01-01", "fbo": fbo_count, "fbs": fbs_count},
            {"date": "2025-01-02", "fbo": fbo_count - 1, "fbs": fbs_count + 1},
            {"date": "2025-01-03", "fbo": fbo_count + 2, "fbs": fbs_count - 1},
        ],
        "cost_by_type": [  # Пример
            {"type": "FBO", "cost": 25000},
            {"type": "FBS", "cost": 20000},
        ]
    }
    return transformed_data

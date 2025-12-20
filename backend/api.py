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

@router.post("/api/sync/trigger", status_code=200)
def trigger_data_sync(request: SyncTriggerRequest, user_id: str = Depends(mock_auth)):
    session_id = db.trigger_sync(user_id)
    return {"message": "Sync started", "session_id": session_id}

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
    if scope == "product" and not sku:
        raise HTTPException(status_code=400, detail="Invalid export scope or missing SKU")

    if scope == "dashboard":
        data = db.get_dashboard_data(user_id, period, logistics)
        if not data:
            raise HTTPException(status_code=404, detail="No data to export")
        export_data = [
            {"metric": "revenue", "value": data["kpi"].revenue},
            {"metric": "orders", "value": data["kpi"].orders},
            {"metric": "avg_check", "value": data["kpi"].avg_check},
            {"metric": "return_rate", "value": data["kpi"].return_rate},
        ]
        filename = f"dashboard_{period}_{logistics}.xlsx"
    elif scope == "top_products":
        data = db.get_dashboard_data(user_id, period, logistics)
        export_data = [
            {"SKU": p.sku, "Name": p.name, "Revenue": p.revenue, "Stock": p.stock, "Logistics": p.logistics}
            for p in data["top_products"]
        ]
        filename = f"top_products_{period}_{logistics}.xlsx"
    elif scope == "product" and sku:
        detail = db.get_product_detail(user_id, sku)
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
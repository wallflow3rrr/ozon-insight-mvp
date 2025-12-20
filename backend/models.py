from pydantic import BaseModel
from typing import List, Optional

# --- Модели для дашборда ---
class KpiData(BaseModel):
    revenue: int
    orders: int
    avg_check: float
    return_rate: float

class ProductSummary(BaseModel):  # ✅ Добавлен
    sku: str
    name: str
    revenue: int
    stock: int
    logistics: str

class DailyMetric(BaseModel):  # ✅ Добавлен
    date: str
    revenue: int
    orders: int
    avg_check: float
    returns: int

class DashboardResponse(BaseModel):  # ✅ Добавлен
    kpi: KpiData
    revenue_chart: List[dict]  # или List[DailyMetric], если хочешь строго
    top_products: List[ProductSummary]

# --- Модель для детализации по товару ---
class ProductDetail(BaseModel):  # ✅ Добавлен
    sku: str
    name: str
    revenue: int
    quantity_sold: int
    stock: int
    sales_chart: List[dict]  # или List[DailyMetric]

class ProductDetailResponse(BaseModel):  # ✅ Добавлен
    sku: str
    name: str
    revenue: int
    quantity_sold: int
    stock: int
    sales_chart: List[dict]

# --- Модель для синхронизации ---
class SyncStatus(BaseModel):  # ✅ Добавлен
    message: str
    session_id: str

# --- Прочие модели, если используются ---
class SyncTriggerRequest(BaseModel):
    pass

class GetDashboardRequest(BaseModel):
    period: int
    logistics: str

class GetProductRequest(BaseModel):
    sku: str
    period: int

class ExportRequest(BaseModel):
    scope: str
    format: str
    period: int
    logistics: str
    sku: Optional[str] = None

class GetMetricTooltipRequest(BaseModel):
    metric_key: str

class ExportResponse(BaseModel):
    message: str
    filename: str
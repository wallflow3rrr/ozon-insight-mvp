from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SyncTriggerRequest(BaseModel):
    user_id: str

class GetDashboardRequest(BaseModel):
    period: int  # 7, 30, 90
    logistics: str  # FBO, FBS, both

class GetProductRequest(BaseModel):
    sku: str
    period: int

class ExportRequest(BaseModel):
    scope: str  # dashboard, top_products, product
    format: str  # xlsx, csv
    period: int
    logistics: str
    sku: Optional[str] = None

class GetMetricTooltipRequest(BaseModel):
    metric_key: str  # revenue, return_rate, avg_check

class SyncStatus(BaseModel):
    last_sync: Optional[datetime] = None
    status: str  # success, error
    message: Optional[str] = None

class KpiData(BaseModel):
    revenue: float
    orders: int
    avg_check: float
    return_rate: float

class ChartDataPoint(BaseModel):
    date: str
    value: float

class Product(BaseModel):
    sku: str
    name: str
    revenue: float
    stock: int
    logistics: str

class DashboardResponse(BaseModel):
    kpi: KpiData
    revenue_chart: List[ChartDataPoint]
    top_products: List[Product]

class ProductDetailResponse(BaseModel):
    sku: str
    name: str
    revenue: float
    quantity_sold: int
    returns: int
    stock: int
    sales_chart: List[ChartDataPoint]

class ExportResponse(BaseModel):
    filename: str
    message: str
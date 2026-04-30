from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class KpiData(BaseModel):
    revenue: float
    orders: int
    avg_check: float
    return_rate: float

class ProductSummary(BaseModel):
    sku: str
    name: str
    revenue: float
    stock: int
    logistics: str

class ChartPoint(BaseModel):
    date: str
    value: float

class DashboardResponse(BaseModel):
    kpi: KpiData
    revenue_chart: List[ChartPoint]
    top_products: List[ProductSummary]

class StockItem(BaseModel):
    sku: str
    name: str
    stock: int
    threshold: int

class WarehouseStock(BaseModel):
    name: str
    stock: int

class StockResponse(BaseModel):
    total_products: int
    total_stock_value: float
    low_stock_count: int
    out_of_stock_count: int
    stock_by_warehouse: List[WarehouseStock]
    low_stock_products: List[StockItem]

class DeliveryChart(BaseModel):
    date: str
    fbo: int
    fbs: int

class CostType(BaseModel):
    type: str
    cost: float

class LogisticsResponse(BaseModel):
    total_orders_fbo: int
    total_orders_fbs: int
    avg_delivery_time_fbo: float
    avg_delivery_time_fbs: float
    total_logistics_cost: float
    logistics_cost_fbo: float
    logistics_cost_fbs: float
    delivery_chart: List[DeliveryChart]
    cost_by_type: List[CostType]

class ProductDetailResponse(BaseModel):
    sku: str
    name: str
    revenue: float
    quantity_sold: int
    stock: int
    sales_chart: List[ChartPoint]

class SyncStatus(BaseModel):
    message: str
    session_id: str

class TooltipResponse(BaseModel):
    label: str
    description: str
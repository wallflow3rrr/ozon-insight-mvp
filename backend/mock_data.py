import random
from datetime import datetime, timedelta
from faker import Faker
from models import KpiData, ChartDataPoint, Product, ProductDetailResponse

fake = Faker()

def generate_date_range(days):
    dates = []
    for i in range(days - 1, -1, -1):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    return dates

def generate_kpi_data(period: int) -> KpiData:
    revenue = random.randint(50000, 500000)
    orders = random.randint(50, 500)
    return KpiData(
        revenue=revenue,
        orders=orders,
        avg_check=round(revenue / orders, 2),
        return_rate=random.randint(0, 15)
    )

def generate_revenue_chart(period: int) -> list[ChartDataPoint]:
    dates = generate_date_range(period)
    return [ChartDataPoint(date=date, value=random.randint(1000, 10000)) for date in dates]

def generate_top_products(limit: int = 5) -> list[Product]:
    products = []
    for _ in range(limit):
        products.append(Product(
            sku=f"SKU{fake.uuid4()[:6]}",
            name=fake.catch_phrase(),
            revenue=random.randint(5000, 50000),
            stock=random.randint(0, 50),
            logistics=random.choice(['FBO', 'FBS'])
        ))
    return products

def generate_product_detail(sku: str) -> ProductDetailResponse:
    dates = generate_date_range(30)
    sales_chart = [ChartDataPoint(date=date, value=random.randint(0, 10)) for date in dates]
    quantity_sold = sum([c.value for c in sales_chart])
    return ProductDetailResponse(
        sku=sku,
        name=fake.catch_phrase(),
        revenue=random.randint(10000, 100000),
        quantity_sold=quantity_sold,
        returns=random.randint(0, 5),
        stock=random.randint(0, 50),
        sales_chart=sales_chart
    )

# --- Хранилище данных (в памяти) ---
class MockDB:
    def __init__(self):
        self.users = {}
        self.sync_sessions = {}
        self.last_syncs = {}
        self.dashboard_data = {}
        self.product_data = {}

    def get_or_create_user(self, user_id: str):
        if user_id not in self.users:
            self.users[user_id] = {"id": user_id, "connected": True}
        return self.users[user_id]

    def trigger_sync(self, user_id: str):
        session_id = f"sess_{fake.uuid4()[:8]}"
        self.sync_sessions[session_id] = {
            "user_id": user_id,
            "started_at": datetime.now(),
            "status": "success"
        }
        period = 30
        self.dashboard_data[user_id] = {
            "kpi": generate_kpi_data(period),
            "revenue_chart": generate_revenue_chart(period),
            "top_products": generate_top_products(5)
        }
        for i in range(20):
            sku = f"SKU{fake.uuid4()[:6]}"
            self.product_data[(user_id, sku)] = generate_product_detail(sku)
        self.last_syncs[user_id] = {
            "last_sync": datetime.now(),
            "status": "success",
            "message": "Mock sync completed"
        }
        return session_id

    def get_dashboard_data(self, user_id: str, period: int, logistics: str):
        data = self.dashboard_data.get(user_id)
        if not data:
            return None
        return data

    def get_product_detail(self, user_id: str, sku: str):
        key = (user_id, sku)
        return self.product_data.get(key)

    def get_sync_status(self, user_id: str):
        return self.last_syncs.get(user_id, {"last_sync": None, "status": "never", "message": "No sync yet"})

db = MockDB()
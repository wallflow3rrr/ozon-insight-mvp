import random
from datetime import datetime, timedelta
from models import (
    # DashboardData,  # ❌ Убрано
    ProductSummary, DailyMetric, ProductDetail, DashboardResponse, ProductDetailResponse
)

# Временная "база данных" в памяти
mock_db = {}

class MockDB:
    def get_or_create_user(self, user_id: str):
        """Создаёт запись для пользователя в 'базе', если её нет."""
        if user_id not in mock_db:
            mock_db[user_id] = {
                "daily_metrics": [],
                "products": {}
            }

    def generate_mock_data(self, user_id: str):
        """Генерирует и сохраняет заглушённые данные для пользователя."""
        # Убедимся, что пользователь существует
        self.get_or_create_user(user_id)

        now = datetime.now()
        start_date = now - timedelta(days=90)
        daily_metrics = []
        products = {}

        for i in range(90):
            date = start_date + timedelta(days=i)
            revenue = random.randint(10000, 50000)
            orders = random.randint(5, 50)
            avg_check = revenue / orders if orders > 0 else 0
            returns = random.randint(0, 5)
            daily_metrics.append(DailyMetric(
                date=date.strftime("%Y-%m-%d"),
                revenue=revenue,
                orders=orders,
                avg_check=avg_check,
                returns=returns
            ))

            for j in range(3):
                sku = f"SKU{j+1}"
                if sku not in products:
                    products[sku] = {
                        "name": f"Товар {j+1}",
                        "revenue": 0,
                        "quantity_sold": 0,
                        "stock": random.randint(0, 100),
                        "logistics": random.choice(["FBO", "FBS"]),
                        "sales_chart": []
                    }
                products[sku]["revenue"] += revenue // 3
                products[sku]["quantity_sold"] += orders // 3

        mock_db[user_id]["daily_metrics"] = daily_metrics
        mock_db[user_id]["products"] = products

    def get_dashboard_data(self, user_id: str, period: int, logistics: str):
        """Возвращает сгенерированные данные за указанный период."""
        user_data = mock_db.get(user_id)
        if not user_data:
            return None

        start_date = datetime.now() - timedelta(days=period)
        filtered_metrics = [
            m for m in user_data["daily_metrics"]
            if datetime.strptime(m.date, "%Y-%m-%d") >= start_date
        ]

        total_revenue = sum(m.revenue for m in filtered_metrics)
        total_orders = sum(m.orders for m in filtered_metrics)
        avg_check = total_revenue / total_orders if total_orders > 0 else 0
        total_returns = sum(m.returns for m in filtered_metrics)
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0

        top_products = sorted(
            user_data["products"].values(),
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]

        top_products_converted = [
            ProductSummary(
                sku=p["name"].replace(" ", ""),
                name=p["name"],
                revenue=p["revenue"],
                stock=p["stock"],
                logistics=p["logistics"]
            )
            for p in top_products
        ]

        return {
            "kpi": {
                "revenue": total_revenue,
                "orders": total_orders,
                "avg_check": round(avg_check, 2),
                "return_rate": round(return_rate, 2)
            },
            "revenue_chart": [{"date": m.date, "value": m.revenue} for m in filtered_metrics[-30:]],
            "top_products": top_products_converted
        }

    def get_product_detail(self, user_id: str, sku: str):
        """Возвращает детализацию по товару."""
        user_data = mock_db.get(user_id)
        if not user_data:
            return None

        product = user_data["products"].get(sku)
        if not product:
            return None

        sales_chart = [
            {"date": m.date, "value": random.randint(1, 10)}
            for m in user_data["daily_metrics"][-30:]
        ]

        return ProductDetail(
            sku=sku,
            name=product["name"],
            revenue=product["revenue"],
            quantity_sold=product["quantity_sold"],
            stock=product["stock"],
            sales_chart=sales_chart
        )

db = MockDB()
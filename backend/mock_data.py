import random
from datetime import datetime, timedelta
from models import (
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
        print(f"DEBUG: generate_mock_data called for user_id={user_id}")  # ✅ Отладка
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

        # Увеличим количество SKU до 5
        for j in range(5):
            sku = f"SKU{j+1}"
            products[sku] = {
                "name": f"Товар {j+1}",
                "revenue": 0,
                "quantity_sold": 0,
                "stock": random.randint(0, 100),
                "logistics": random.choice(["FBO", "FBS"]),
                "sales_chart": []
            }

        # Распределяем выручку и заказы между товарами
        for metric in daily_metrics:
            for sku in products:
                products[sku]["revenue"] += random.randint(1000, 5000)
                products[sku]["quantity_sold"] += random.randint(1, 10)

        print(f"DEBUG: Generated daily_metrics count: {len(daily_metrics)}")  # ✅ Отладка
        print(f"DEBUG: Generated products count: {len(products)}")  # ✅ Отладка
        print(f"DEBUG: Generated products: {products}")  # ✅ Отладка

        mock_db[user_id]["daily_metrics"] = daily_metrics
        mock_db[user_id]["products"] = products

        print(f"DEBUG: Saved to DB for user {user_id}: daily_metrics={len(mock_db[user_id]['daily_metrics'])}, products={len(mock_db[user_id]['products'])}")  # ✅ Отладка

    def get_dashboard_data(self, user_id: str, period: int, logistics: str):
        """Возвращает сгенерированные данные за указанный период."""
        print(f"DEBUG: get_dashboard_data called with user_id={user_id}, period={period}, logistics={logistics}")  # ✅ Отладка
        self.get_or_create_user(user_id)

        user_data = mock_db.get(user_id)
        print(f"DEBUG: User data in DB: {user_data}")  # ✅ Отладка
        if not user_data:
            print("DEBUG: User data is None or empty after get_or_create_user")  # ✅ Отладка
            return None

        start_date = datetime.now() - timedelta(days=period)
        filtered_metrics = [
            m for m in user_data["daily_metrics"]
            if datetime.strptime(m.date, "%Y-%m-%d") >= start_date
        ]
        print(f"DEBUG: Filtered metrics count: {len(filtered_metrics)}")  # ✅ Отладка

        # ✅ Фильтруем товары по логистике
        filtered_products = {}
        for sku, data in user_data["products"].items():
            if logistics == "both" or data["logistics"] == logistics:
                filtered_products[sku] = data
        print(f"DEBUG: Filtered products count: {len(filtered_products)}")  # ✅ Отладка

        if not filtered_products:
            print("DEBUG: No products after logistics filter")  # ✅ Отладка
            return None

        # Агрегируем метрики по отфильтрованным товарам
        total_revenue = sum(p["revenue"] for p in filtered_products.values())
        total_orders = sum(p["quantity_sold"] for p in filtered_products.values())
        avg_check = total_revenue / total_orders if total_orders > 0 else 0
        total_returns = sum(m.returns for m in filtered_metrics)
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0

        # Формируем список ТОП-5 товаров из отфильтрованных
        top_products = sorted(
            filtered_products.values(),
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

        result = {
            "kpi": {
                "revenue": total_revenue,
                "orders": total_orders,
                "avg_check": round(avg_check, 2),
                "return_rate": round(return_rate, 2)
            },
            "revenue_chart": [{"date": m.date, "value": m.revenue} for m in filtered_metrics[-30:]],
            "top_products": top_products_converted
        }
        print(f"DEBUG: Returning dashboard data: {result}")  # ✅ Отладка
        return result

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
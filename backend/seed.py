import csv
import os
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal

from database import SessionLocal, engine
from models_db import (
    Base, User, Tokens, Products, Orders, Returns, MetricsSummary, SyncHistory
)

# Путь для сохранения CSV
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Реалистичные товары (с вашего скриншота)
PRODUCTS_SEED = [
    {"sku": "184920374", "name": "Ароматизатор в машину + полотенце", "price": 606, "logistics": "FBO"},
    {"sku": "193847562", "name": "Килт-полотенце для женщин", "price": 753, "logistics": "FBS"},
    {"sku": "201938475", "name": "Полотенце банное микрофибра", "price": 670, "logistics": "FBO"},
    {"sku": "184756392", "name": "Набор кремов для рук 5 шт", "price": 429, "logistics": "FBS"},
    {"sku": "192837465", "name": "Подарочный набор полотенец", "price": 478, "logistics": "FBO"},
    {"sku": "209384756", "name": "Махровые полотенца 2 шт", "price": 536, "logistics": "FBS"},
    {"sku": "198273645", "name": "Набор полотенец вафельные 12 шт", "price": 1013, "logistics": "FBO"},
]

RETURN_REASONS = ["Не подошёл размер", "Брак", "Не понравилось качество", "Отказ покупателя", "Повреждена упаковка"]

# ✅ ВАЖНО: Используем валидный UUID для тестового пользователя
USER_ID = "00000000-0000-0000-0000-000000000001"

def generate_csv_files(days: int = 90):
    """Генерирует CSV файлы"""
    orders_path = os.path.join(DATA_DIR, "orders.csv")
    returns_path = os.path.join(DATA_DIR, "returns.csv")
    stocks_path = os.path.join(DATA_DIR, "stocks.csv")
    
    start_date = date.today() - timedelta(days=days)
    
    with open(orders_path, "w", newline="", encoding="utf-8") as f_ord, \
         open(returns_path, "w", newline="", encoding="utf-8") as f_ret, \
         open(stocks_path, "w", newline="", encoding="utf-8") as f_stk:
        
        w_ord = csv.writer(f_ord)
        w_ord.writerow(["order_id", "date", "sku", "product_name", "quantity", "price", "revenue", "status", "logistics_type"])
        
        w_ret = csv.writer(f_ret)
        w_ret.writerow(["order_id", "sku", "quantity", "amount", "reason", "date"])
        
        w_stk = csv.writer(f_stk)
        w_stk.writerow(["sku", "name", "logistics_type", "stock", "reserved", "updated_at"])
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            daily_orders = random.randint(5, 25)
            
            for _ in range(daily_orders):
                prod = random.choice(PRODUCTS_SEED)
                qty = random.randint(1, 3)
                price = prod["price"]
                revenue = Decimal(str(qty * price))
                status = random.choices(["delivered", "cancelled", "awaiting_packaging"], weights=[0.85, 0.10, 0.05])[0]
                order_id = f"ORD-{current_date.strftime('%y%m%d')}-{random.randint(10000, 99999)}"
                
                w_ord.writerow([
                    order_id, current_date.strftime("%d.%m.%Y"), prod["sku"], prod["name"],
                    qty, f"{price:.2f}", f"{revenue:.2f}", status, prod["logistics"]
                ])
                
                if random.random() < 0.12 and status == "delivered":
                    ret_qty = random.randint(1, qty)
                    ret_amount = Decimal(str(ret_qty * price * 0.9))
                    w_ret.writerow([
                        order_id, prod["sku"], ret_qty, f"{ret_amount:.2f}",
                        random.choice(RETURN_REASONS), current_date.strftime("%d.%m.%Y")
                    ])
        
        for i, prod in enumerate(PRODUCTS_SEED):
            # Первые 2 товара - низкий остаток
            if i < 2: stock = random.randint(0, 8)
            # Третий - нет в наличии
            elif i == 2: stock = 0
            # Остальные - нормальный
            else: stock = random.randint(50, 200)
            
            reserved = random.randint(0, max(0, stock // 4))
            w_stk.writerow([prod["sku"], prod["name"], prod["logistics"], stock, reserved, date.today().strftime("%d.%m.%Y")])

def seed_database():
    """Загружает данные из CSV в PostgreSQL"""
    db = SessionLocal()
    try:
        # 1. Создаем пользователя, если нет
        user = db.query(User).filter(User.id == USER_ID).first()
        if not user:
            user = User(id=USER_ID, ozon_seller_id="OZON_SELLER_999")
            db.add(user)
            db.flush()
            
            token = Tokens(
                user_id=USER_ID,
                access_token="ozon_live_abc123...",
                refresh_token="ozon_refresh_xyz...",
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.add(token)

        # 2. Загружаем товары из stocks.csv
        stocks_path = os.path.join(DATA_DIR, "stocks.csv")
        if os.path.exists(stocks_path):
            with open(stocks_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prod = db.query(Products).filter(Products.sku == row["sku"]).first()
                    if not prod:
                        prod = Products(
                            user_id=USER_ID, sku=row["sku"], name=row["name"],
                            logistics_type=row["logistics_type"], stock=int(row["stock"])
                        )
                        db.add(prod)
                    else:
                        prod.stock = int(row["stock"])
            db.flush()

        # 3. Загружаем заказы
        orders_path = os.path.join(DATA_DIR, "orders.csv")
        if os.path.exists(orders_path):
            with open(orders_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Проверяем дубликаты
                    if db.query(Orders).filter(Orders.order_id == row["order_id"]).first():
                        continue
                    
                    order_date = datetime.strptime(row["date"], "%d.%m.%Y").date()
                    db.add(Orders(
                        user_id=USER_ID, order_id=row["order_id"], sku=row["sku"],
                        quantity=int(row["quantity"]), revenue=Decimal(row["revenue"]),
                        status=row["status"], date=order_date,
                        logistics_type=row["logistics_type"]
                    ))
                    count += 1
                print(f"✅ Загружено заказов: {count}")

        # 4. Загружаем возвраты
        returns_path = os.path.join(DATA_DIR, "returns.csv")
        if os.path.exists(returns_path):
            with open(returns_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    ret_date = datetime.strptime(row["date"], "%d.%m.%Y").date()
                    db.add(Returns(
                        user_id=USER_ID, order_id=row["order_id"], sku=row["sku"],
                        quantity=int(row["quantity"]), amount=Decimal(row["amount"]),
                        reason=row["reason"], date=ret_date
                    ))
                    count += 1
                print(f"✅ Загружено возвратов: {count}")

        db.commit()
        print("✅ База данных успешно наполнена!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении БД: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Запуск генерации CSV...")
    generate_csv_files()
    print("🚀 Запуск заполнения БД...")
    seed_database()
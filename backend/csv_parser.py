import csv
import os
from datetime import date, datetime
from decimal import Decimal
from database import SessionLocal
from models_db import User, Tokens, Products, Orders, Returns

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USER_ID = "mock_user_123"

def parse_and_load_csv():
    db = SessionLocal()
    try:
        # Создаём пользователя и токены, если их нет
        if not db.query(User).filter(User.id == USER_ID).first():
            db.add(User(id=USER_ID, ozon_seller_id="OZON_SELLER_999"))
            db.add(Tokens(
                user_id=USER_ID,
                access_token="ozon_live_abc123def456...",
                refresh_token="ozon_refresh_xyz789...",
                expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            ))
            db.commit()

        products_map = {}
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
                    products_map[row["sku"]] = prod

        orders_path = os.path.join(DATA_DIR, "orders.csv")
        returns_path = os.path.join(DATA_DIR, "returns.csv")
        
        # ✅ ПАРСИНГ ЗАКАЗОВ С УЧЁТОМ ФОРМАТА ДД.ММ.ГГГГ
        if os.path.exists(orders_path):
            with open(orders_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if db.query(Orders).filter(Orders.order_id == row["order_id"]).first():
                        continue
                    
                    parsed_date = datetime.strptime(row["date"], "%d.%m.%Y").date()
                    
                    db.add(Orders(
                        user_id=USER_ID, 
                        order_id=row["order_id"], 
                        sku=row["sku"],
                        quantity=int(row["quantity"]), 
                        revenue=Decimal(row["revenue"]),
                        status=row["status"], 
                        date=parsed_date,
                        logistics_type=row["logistics_type"]
                    ))
        
        # ✅ ПАРСИНГ ВОЗВРАТОВ С УЧЁТОМ ФОРМАТА ДД.ММ.ГГГГ
        if os.path.exists(returns_path):
            with open(returns_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parsed_date = datetime.strptime(row["date"], "%d.%m.%Y").date()
                    
                    db.add(Returns(
                        user_id=USER_ID, 
                        order_id=row["order_id"], 
                        sku=row["sku"],
                        quantity=int(row["quantity"]), 
                        amount=Decimal(row["amount"]),
                        reason=row["reason"], 
                        date=parsed_date
                    ))
                    
        db.commit()
        print("✅ CSV распарсены и загружены в БД")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка парсинга: {e}")
    finally:
        db.close()
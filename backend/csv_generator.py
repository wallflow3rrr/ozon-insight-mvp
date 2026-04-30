import csv
import random
import os
from datetime import datetime, timedelta, date
from decimal import Decimal

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Реалистичные товары с вашего скриншота
PRODUCTS = [
    {"sku": "184920374", "name": "Ароматизатор в машину + полотенце", "price": 606, "logistics": "FBO"},
    {"sku": "193847562", "name": "Килт-полотенце для женщин", "price": 753, "logistics": "FBS"},
    {"sku": "201938475", "name": "Полотенце банное микрофибра", "price": 670, "logistics": "FBO"},
    {"sku": "184756392", "name": "Набор кремов для рук 5 шт", "price": 429, "logistics": "FBS"},
    {"sku": "192837465", "name": "Подарочный набор полотенец", "price": 478, "logistics": "FBO"},
    {"sku": "209384756", "name": "Махровые полотенца 2 шт", "price": 536, "logistics": "FBS"},
    {"sku": "198273645", "name": "Набор полотенец вафельные 12 шт", "price": 1013, "logistics": "FBO"},
]

RETURN_REASONS = ["Не подошёл размер", "Брак", "Не понравилось качество", "Отказ покупателя", "Повреждена упаковка"]

def generate_csv_files(days: int = 90):
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
                prod = random.choice(PRODUCTS)
                qty = random.randint(1, 3)
                price = prod["price"]
                revenue = Decimal(str(qty * price))
                status = random.choices(["delivered", "cancelled", "awaiting_packaging"], weights=[0.85, 0.10, 0.05])[0]
                order_id = f"ORD-{current_date.strftime('%y%m%d')}-{random.randint(10000, 99999)}"
                
                w_ord.writerow([
                    order_id, 
                    current_date.strftime("%d.%m.%Y"),
                    prod["sku"], 
                    prod["name"],
                    qty, 
                    f"{price:.2f}",
                    f"{revenue:.2f}", 
                    status, 
                    prod["logistics"]
                ])
                
                if random.random() < 0.12 and status == "delivered":
                    ret_qty = random.randint(1, qty)
                    ret_amount = Decimal(str(ret_qty * price * 0.9))
                    w_ret.writerow([
                        order_id, 
                        prod["sku"], 
                        ret_qty, 
                        f"{ret_amount:.2f}",
                        random.choice(RETURN_REASONS), 
                        current_date.strftime("%d.%m.%Y")
                    ])
        
        # ✅ ИСПРАВЛЕНИЕ: Добавляем товары с разным уровнем остатка
        for i, prod in enumerate(PRODUCTS):
            # ✅ Первые 2 товара — низкий остаток (< 10)
            if i < 2:
                stock = random.randint(0, 8)  # 0-8 штук (низкий остаток)
            # ✅ Третий товар — совсем нет в наличии
            elif i == 2:
                stock = 0  # Нет в наличии
            # ✅ Остальные — нормальный остаток
            else:
                stock = random.randint(50, 200)
                
            reserved = random.randint(0, max(0, stock // 4))
            w_stk.writerow([
                prod["sku"], 
                prod["name"], 
                prod["logistics"], 
                stock, 
                reserved, 
                date.today().strftime("%d.%m.%Y")
            ])
            
    print(f"✅ CSV-файлы созданы в {DATA_DIR}")
from database import SessionLocal
from models_db import Orders, Returns, MetricsSummary
from datetime import date, timedelta
from decimal import Decimal

USER_ID = "00000000-0000-0000-0000-000000000001"

def calculate_and_save_metrics():
    db = SessionLocal()
    try:
        # Очищаем старые метрики
        db.query(MetricsSummary).filter(MetricsSummary.user_id == USER_ID).delete()
        
        # Берём все заказы за последние 90 дней
        start_date = date.today() - timedelta(days=90)
        orders = db.query(Orders).filter(
            Orders.user_id == USER_ID,
            Orders.date >= start_date
        ).all()
        
        returns = db.query(Returns).filter(
            Returns.user_id == USER_ID,
            Returns.date >= start_date
        ).all()
        
        # Группируем по датам
        from collections import defaultdict
        daily = defaultdict(lambda: {"revenue": Decimal("0"), "orders": 0, "returns": 0})
        
        for o in orders:
            daily[o.date]["revenue"] += o.revenue
            daily[o.date]["orders"] += 1
            
        for r in returns:
            daily[r.date]["returns"] += r.quantity
            
        # Сохраняем метрики
        for d, data in daily.items():
            avg_check = data["revenue"] / data["orders"] if data["orders"] > 0 else Decimal("0")
            ret_rate = (data["returns"] / data["orders"] * 100) if data["orders"] > 0 else Decimal("0")
            
            for l_type in ["FBO", "FBS", "both"]:
                db.add(MetricsSummary(
                    user_id=USER_ID,
                    date=d,
                    revenue=data["revenue"],
                    orders_count=data["orders"],
                    avg_check=avg_check,
                    returns_count=data["returns"],
                    return_rate=ret_rate,
                    logistics_type=l_type
                ))
                
        db.commit()
        print("✅ Метрики рассчитаны и сохранены!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    calculate_and_save_metrics()
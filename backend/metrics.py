from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from database import SessionLocal
from models_db import Orders, Returns, MetricsSummary

def calculate_daily_metrics(user_id: str, days: int = 90):
    db = SessionLocal()
    try:
        start_date = date.today() - timedelta(days=days)
        
        db.query(MetricsSummary).filter(MetricsSummary.user_id == user_id).delete()
        
        current = start_date
        while current <= date.today():
            next_day = current + timedelta(days=1)
            
            orders = db.query(Orders).filter(
                Orders.user_id == user_id, Orders.date >= current, Orders.date < next_day
            ).all()
            
            returns = db.query(Returns).filter(
                Returns.user_id == user_id, Returns.date >= current, Returns.date < next_day
            ).all()
            
            revenue = sum(o.revenue for o in orders)
            orders_count = len(orders)
            returns_count = sum(r.quantity for r in returns)
            avg_check = revenue / orders_count if orders_count > 0 else Decimal("0.00")
            return_rate = (returns_count / orders_count * 100) if orders_count > 0 else Decimal("0.00")
            
            # Агрегируем по логистике
            for l_type in ["FBO", "FBS", "both"]:
                if l_type == "both":
                    l_orders = orders
                else:
                    l_orders = [o for o in orders if o.logistics_type == l_type]
                    
                l_rev = sum(o.revenue for o in l_orders)
                l_count = len(l_orders)
                l_ret = sum(r.quantity for r in returns if any(o.order_id == r.order_id for o in l_orders))
                l_avg = l_rev / l_count if l_count > 0 else Decimal("0.00")
                l_rate = (l_ret / l_count * 100) if l_count > 0 else Decimal("0.00")
                
                db.add(MetricsSummary(
                    user_id=user_id, date=current,
                    revenue=l_rev, orders_count=l_count,
                    avg_check=l_avg, returns_count=l_ret,
                    return_rate=l_rate, logistics_type=l_type
                ))
            current = next_day
            
        db.commit()
        print("✅ Метрики пересчитаны")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка расчёта метрик: {e}")
    finally:
        db.close()
from database import SessionLocal
from jwt_utils import get_password_hash
from models_db import User

db = SessionLocal()

try:
    # Ищем по тому ID, который реально сейчас в БД
    admin = db.query(User).filter(User.ozon_seller_id == "admin_internal_user").first()
    
    if admin:
        new_login = "Spgroup777@yandex.ru"
        new_password = "Spgroup777@yandex.ru"
        
        # Обновляем логин (ozon_seller_id) и пароль
        admin.ozon_seller_id = new_login
        admin.hashed_password = get_password_hash(new_password)
        
        db.commit()
        print("✅ Данные администратора успешно обновлены!")
        print(f"   Новый логин: {new_login}")
        print(f"   Новый пароль: {new_password}")
        print("\n🔑 Теперь на сайте вводи логин: Spgroup777@yandex.ru")
    else:
        print("❌ Пользователь с ozon_seller_id='admin_internal_user' не найден!")
        print("💡 Возможно, в БД записано 'admin_internal_user1'. Проверь точное название.")
        
except Exception as e:
    db.rollback()
    print(f"❌ Ошибка: {e}")
finally:
    db.close()
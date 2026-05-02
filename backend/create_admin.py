"""
Скрипт для создания пользователя-администратора в базе данных.
Данные для входа берутся из переменных окружения (.env).
Запускается ОДИН РАЗ после настройки авторизации.
"""
import os
from database import SessionLocal, engine
from models_db import User, Base
from jwt_utils import get_password_hash
from dotenv import load_dotenv
import uuid

# Загружаем переменные из .env
load_dotenv()

def create_admin_user():
    """Создаёт пользователя из переменных окружения"""
    
    # Читаем настройки из .env
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
    ADMIN_OZON_ID = os.getenv("ADMIN_OZON_ID", "admin_internal_user")
    
    # Проверяем, что таблицы существуют
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Проверяем, не создан ли уже админ
        existing = db.query(User).filter(User.ozon_seller_id == ADMIN_OZON_ID).first()
        if existing:
            print(f"⚠️  Пользователь '{ADMIN_USERNAME}' уже существует (ID: {existing.id})")
            print("✅ Ничего не меняем. Для смены пароля удалите запись вручную в pgAdmin.")
            return
        
        # Хешируем пароль
        hashed_pw = get_password_hash(ADMIN_PASSWORD)
        print(f"🔐 Хеш пароля: {hashed_pw[:20]}...")
        
        # Создаём нового пользователя
        new_user = User(
            id=uuid.uuid4(),
            ozon_seller_id=ADMIN_OZON_ID,  # Используем как уникальный "логин" в БД
            hashed_password=hashed_pw
        )
        
        db.add(new_user)
        db.commit()
        
        print(f"✅ Пользователь '{ADMIN_USERNAME}' успешно создан!")
        print(f"   ID: {new_user.id}")
        print(f"   Логин: {ADMIN_USERNAME}")
        print(f"   Пароль: {'*' * len(ADMIN_PASSWORD)}")  # Не выводим пароль в консоль
        print("\n🔑 Теперь можно войти в систему с этими данными.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании пользователя: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
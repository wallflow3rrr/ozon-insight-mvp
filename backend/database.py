from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем URL подключения к БД из переменной окружения
# Если переменная не задана — используем значение по умолчанию
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ozoninsight_db"
)

# Создаём движок SQLAlchemy для подключения к PostgreSQL
# pool_pre_ping=True — проверяет соединение перед использованием (защита от разорванных соединений)
# pool_recycle=3600 — обновляет соединения каждые 3600 секунд (защита от таймаутов БД)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Создаём фабрику сессий для работы с БД
# autocommit=False — транзакции управляются вручную
# autoflush=False — изменения не сбрасываются в БД автоматически до commit()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для всех моделей SQLAlchemy
# От него будут наследоваться все модели данных (User, Orders, Products и т.д.)
Base = declarative_base()


def get_db():
    """
    Зависимость FastAPI для получения сессии базы данных.
    
    Используется в эндпоинтах через Depends(get_db).
    Автоматически закрывает соединение после завершения запроса.
    
    Yields:
        Session: Активная сессия SQLAlchemy для работы с БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
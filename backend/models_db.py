import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, DateTime, Date, DECIMAL, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID  # ✅ Добавлено для PostgreSQL
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ozon_seller_id = Column(String, nullable=False, unique=True)  # ✅ Добавлено unique=True
    hashed_password = Column(String, nullable=False)              # ✅ НОВОЕ ПОЛЕ ДЛЯ ХЕША
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tokens = relationship("Tokens", back_populates="user", uselist=False, cascade="all, delete-orphan")
    products = relationship("Products", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Orders", back_populates="user", cascade="all, delete-orphan")
    returns = relationship("Returns", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("MetricsSummary", back_populates="user", cascade="all, delete-orphan")
    sync_history = relationship("SyncHistory", back_populates="user", cascade="all, delete-orphan")

class Tokens(Base):
    __tablename__ = "tokens"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="tokens")

class Products(Base):
    __tablename__ = "products"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sku = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    logistics_type = Column(String, nullable=False)  # FBO или FBS
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="products")

class Orders(Base):
    __tablename__ = "orders"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    revenue = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    logistics_type = Column(String, nullable=False)
    
    user = relationship("User", back_populates="orders")

class Returns(Base):
    __tablename__ = "returns"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String)
    date = Column(Date, nullable=False, index=True)
    
    user = relationship("User", back_populates="returns")

class MetricsSummary(Base):
    __tablename__ = "metrics_summary"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    revenue = Column(DECIMAL(10, 2), nullable=False)
    orders_count = Column(Integer, nullable=False)
    avg_check = Column(DECIMAL(10, 2))
    returns_count = Column(Integer, default=0)
    return_rate = Column(DECIMAL(5, 2))
    logistics_type = Column(String, nullable=False)
    
    user = relationship("User", back_populates="metrics")

class SyncHistory(Base):
    __tablename__ = "sync_history"
    
    # ✅ Тип UUID для первичного ключа
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ✅ Внешний ключ тоже UUID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String, nullable=False)
    error_message = Column(Text)
    
    user = relationship("User", back_populates="sync_history")
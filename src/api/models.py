# src/api/models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base  # ← ИМПОРТИРУЕМ ОБЩИЙ Base из database.py
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # ✅ FIX: добавляем default
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Отношение выносится внутрь класса
    transactions = relationship("Transaction", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Новое поле: 'income' или 'expense'
    type = Column(String(20), nullable=False, default='expense')
    
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String(20), nullable=False, default='card')

    user = relationship("User", back_populates="transactions")
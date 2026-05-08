# src/api/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = глобальная категория
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    type = Column(Enum(TransactionType), nullable=False)
    payment_method = Column(String, nullable=True)
    
    # 🔧 FIX: Добавлены server_default для created_at
    created_at = Column(
        DateTime, 
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
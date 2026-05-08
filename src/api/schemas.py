# src/api/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# === User Schemas ===

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Token Schemas ===

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# === Category Schemas ===

class CategoryBase(BaseModel):
    name: str
    type: TransactionType


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Transaction Schemas ===

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)  # Должно быть больше 0
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    type: TransactionType
    payment_method: Optional[str] = None


class TransactionCreate(TransactionBase):
    # 🔧 FIX: category может быть строкой (названием) или ID
    category: Optional[str] = None
    category_id: Optional[int] = None


class TransactionOut(TransactionBase):
    id: int
    user_id: int
    category_id: Optional[int] = None
    # 🔧 FIX: created_at с default_factory
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    category: Optional[CategoryOut] = None

    model_config = ConfigDict(from_attributes=True)
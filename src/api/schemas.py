# src/api/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, Literal

# --- Транзакции ---
class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)  # 🔐 Сумма строго больше 0
    category: str = Field(..., min_length=1, max_length=100)  # 🔐 Длина категории
    description: Optional[str] = Field(default="", max_length=500)  # 🔐 Лимит описания
    date: date
    type: Literal['income', 'expense'] = 'expense'
    payment_method: Literal['cash', 'card'] = 'card'

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}

# --- Пользователи ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # 🔐 Мин. длина пароля 8 символов

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str
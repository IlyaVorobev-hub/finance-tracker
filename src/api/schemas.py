# src/api/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from typing import Literal, Optional

# --- Транзакции ---
class TransactionBase(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
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

# --- Пользователи (добавлено) ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

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
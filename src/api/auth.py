# src/api/auth.py
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import database, models  # Импорт ваших моделей и БД

# === НАСТРОЙКИ БЕЗОПАСНОСТИ ===
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set!")

# 🔐 Контекст хеширования (bcrypt с 12 раундами)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# === ВЕРИФИКАЦИЯ ПАРОЛЯ ===
def validate_password(password: str) -> bool:
    """Проверка сложности пароля"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # Заглавная буква
        return False
    if not re.search(r"[a-z]", password):  # Строчная буква
        return False
    if not re.search(r"\d", password):      # Цифра
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): # Спецсимвол
        return False
    return True

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# === JWT ТОКЕНЫ ===
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # 🔐 Используем UTC время, чтобы избежать рассинхрона
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === ПОЛУЧЕНИЕ ПОЛЬЗОВАТЕЛЯ ===
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """Безопасное извлечение пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
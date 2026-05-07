# src/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# ✅ Абсолютные импорты (избегаем циклических импортов)
from src.api import models, schemas, database
from src.api.auth import (  # 🔧 Импортируем как auth_utils
    authenticate_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password
)
from src.api.limiter import limiter

router = APIRouter(tags=["auth"])


# 🔐 Стандартный OAuth2 токен-эндпоинт (для Swagger /token)
@router.post("/token", response_model=schemas.Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """Получение JWT токена (OAuth2 стандарт)"""
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# 🔐 Альтернативный логин-эндпоинт (если нужен отдельный от /token)
@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """Альтернативный вход (можно удалить, если используется только /token)"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ➕ Эндпоинт регистрации
@router.post("/register", response_model=schemas.UserOut)
@limiter.limit("3/minute")  # Строже лимит для регистрации (защита от спама)
async def register(
    request: Request,
    user_in: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    """Регистрация нового пользователя"""
    # Проверка: не занят ли email
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание пользователя
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Опционально: сразу выдаём токен после регистрации
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
# src/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# ✅ Абсолютные импорты
from src.api import models, schemas, database
from src.api.auth import (  # ← импортируем функции из утилит
    authenticate_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    validate_password
)
from src.api.limiter import limiter

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.Token)
@limiter.limit("10/minute")
async def register(
    request: Request,
    user_in: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    """Регистрация нового пользователя"""
    if not validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Пароль слишком слабый. Требуется: 8+ символов, заглавные, строчные, цифры и спецсимволы."
        )

    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=schemas.Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """OAuth2 стандартный токен-эндпоинт"""
    user = authenticate_user(db, form.username, form.password)
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
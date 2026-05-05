# src/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# 🔐 ИМПОРТЫ
from .. import models, schemas, database, auth
from ..limiter import limiter  # ← ИМПОРТ ИЗ НОВОГО ФАЙЛА (без циклической зависимости)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.Token)
@limiter.limit("10/minute")  # Не более 10 регистраций в минуту с одного IP
def register(
    request: Request,
    user_in: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    # Проверка сложности пароля
    if not auth.validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Пароль слишком слабый. Требуется: 8+ символов, заглавные, строчные, цифры и спецсимволы."
        )

    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        hashed_password=auth.get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")  # 🔐 Не более 5 попыток входа в минуту с одного IP
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),  # ✅ ИСПРАВЛЕНО: двоеточие и правильное имя
    db: Session = Depends(database.get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
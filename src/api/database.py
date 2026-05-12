# src/api/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# 🔧 Получаем DATABASE_URL из окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# 🔧 Настройки подключения для Render/PostgreSQL
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Важно для serverless-окружений
    connect_args={"sslmode": "require"} if "postgresql" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Зависимость FastAPI для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Безопасное создание таблиц (идемпотентное)"""
    # Импортируем модели здесь, чтобы избежать циклических импортов
    from src.api import models  # noqa: F401
    
    # Создаём таблицы, если их нет (не ломает существующие)
    Base.metadata.create_all(bind=engine)
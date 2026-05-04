# src/api/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем локальные переменные из .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔐 Безопасный фолбэк для локальной разработки
if not DATABASE_URL:
    # На Render переменная обязательна
    if os.getenv("RENDER") == "true":
        raise ValueError(" DATABASE_URL is required in production!")
    DATABASE_URL = "sqlite:///./finance_local.db"
    print("⚠️ Running with local SQLite database.")

# 🔐 Принудительный SSL для PostgreSQL
if DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql"):
    if "?sslmode=" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

# Создаём движок с проверкой здоровья соединения
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед запросом
    pool_recycle=3600    # Пересоздаёт соединение раз в час (защита от таймаутов)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Безопасное получение сессии с гарантированным закрытием"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
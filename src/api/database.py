# src/api/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Отладка: выводим, что видит код
print("=" * 50)
print("DEBUG: Checking environment variables...")
print(f"DATABASE_URL exists: {os.getenv('DATABASE_URL') is not None}")
if os.getenv('DATABASE_URL'):
    db_url = os.getenv('DATABASE_URL')
    print(f"DATABASE_URL starts with: {db_url[:20]}...")
    print(f"Is postgres: {db_url.startswith('postgres://')}")
else:
    print("❌ DATABASE_URL is EMPTY or NOT SET!")
print("=" * 50)

# Сначала пробуем загрузить из .env (для локальной разработки)
load_dotenv()

# Читаем DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Если переменной нет — ошибка (не молча падаем на SQLite!)
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables!")

# Для PostgreSQL добавляем параметры подключения, если их нет
if DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"):
    if "?sslmode=" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

# Создаём движок
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
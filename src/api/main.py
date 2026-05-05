# src/api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

# 🔐 ИМПОРТ лимитера из отдельного файла (избегаем циклических импортов)
from .limiter import limiter
from .routers import auth, transactions
from .database import engine, Base

# === ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ===
app = FastAPI(
    title="Finance Tracker API",
    description="Защищённый персональный финансовый трекер",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# 🔗 Прикрепляем лимитер к приложению (обязательно для работы @limiter.limit)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, RateLimitExceeded)

# === 🔐 CORS (Cross-Origin Resource Sharing) ===
# Разрешаем запросы только с доверенных источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Локальная разработка (Streamlit)
        "https://finance-tracker-frontend-1h1m.onrender.com",  # Публичный фронтенд
        "https://finance-tracker-api-q1qg.onrender.com"  # Сам API (для Swagger/docs)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# === ПОДКЛЮЧЕНИЕ РОУТЕРОВ ===
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])

# === HEALTH CHECK (проверка работоспособности) ===
@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "Finance Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# === ПРОСТАЯ ПРОВЕРКА БД (опционально) ===
@app.get("/health/db")
def health_db():
    """Проверка подключения к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"database": "connected", "status": "ok"}
    except Exception as e:
        return {"database": "error", "status": "fail", "error": str(e)}

# === СОЗДАНИЕ ТАБЛИЦ ПРИ ЗАПУСКЕ (если миграции не сработали) ===
# ⚠️ В продакшене лучше полагаться только на Alembic
@app.on_event("startup")
def startup_event():
    """
    Инициализация при старте приложения.
    Создаёт таблицы, если их ещё нет (для первого запуска).
    """
    # Base.metadata.create_all(bind=engine)  # ← Раскомментируйте, если таблицы не создаются через Alembic
    pass
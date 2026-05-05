# src/api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import auth, transactions
from .database import engine, Base

# === ИНИЦИАЛИЗАЦИЯ ===
app = FastAPI(title="Finance Tracker API", version="1.0.0")

# Настраиваем лимитер
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# === 🔐 CORS (ЗАШИЛИ АДРЕС В КОД, ЧТОБЫ НЕ ЗАВИСЕТЬ ОТ RENDER) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Для локального Streamlit
        "https://finance-tracker-frontend.onrender.com", 
        "https://finance-tracker-api-q1qg.onrender.com" # Для вашего API (чтобы Swagger работал)
        # Сюда можно будет добавить адрес фронтенда, когда задеплоите его
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Роуты ===
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(transactions.router, prefix="/api/v1/transactions")

# Проверка здоровья сервиса
@app.get("/")
def read_root():
    return {"status": "ok", "service": "Finance Tracker API"}

# Автоматическое создание таблиц при первом запуске (на случай, если миграции не сработали)
@app.on_event("startup")
def startup():
    # Base.metadata.create_all(bind=engine)  # Закомментируйте, если используете Alembic!
    pass
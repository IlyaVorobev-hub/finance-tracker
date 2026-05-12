# src/api/main.py — начало файла
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.database import engine, Base, init_db  # ← добавь init_db
from src.api.routers import auth, transactions

# === Инициализация приложения ===
app = FastAPI(
    title="Finance Tracker API",
    description="API для учёта личных финансов",
    version="1.0.0"
)

# 🔧 Вызываем безопасное создание таблиц при старте
@app.on_event("startup")
def on_startup():
    init_db()

# === CORS ===
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Роутеры ===
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(transactions.router, prefix="/api/v1/transactions")

# === Health check ===
@app.get("/health")
def health():
    return {"status": "healthy", "service": "finance-tracker-api"}

@app.get("/")
def root():
    return {"message": "Finance Tracker API is running"}
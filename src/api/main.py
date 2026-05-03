# src/api/main.py
from fastapi import FastAPI
from .routers import transactions, auth  # ← импортируем оба роутера

app = FastAPI(title="Finance Tracker", version="0.2.0")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])  # ← авторизация
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])  # ← транзакции

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "finance-tracker"}

@app.get("/")
def root():
    return {"message": "Finance Tracker API", "docs": "/docs"}
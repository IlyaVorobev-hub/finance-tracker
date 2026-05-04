# src/api/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

# 🔐 ИМПОРТЫ: .. = выйти из routers в api
from .. import models, schemas, database, auth

router = APIRouter(tags=["transactions"])

@router.get("/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100,
    tx_type: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id  # 🔐 ИЗОЛЯЦИЯ
    )
    
    if tx_type:
        query = query.filter(models.Transaction.type == tx_type)
    if year:
        query = query.filter(models.Transaction.date >= date(year, 1, 1))
        query = query.filter(models.Transaction.date <= date(year, 12, 31))
    if month:
        query = query.filter(models.Transaction.date.month == month)
    if category and category != "Все":
        query = query.filter(models.Transaction.category == category)
        
    return query.offset(skip).limit(limit).all()

@router.get("/summary")
def read_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    tx_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id  # 🔐 ИЗОЛЯЦИЯ
    )
    
    if tx_type and tx_type != "Все":
        query = query.filter(models.Transaction.type == tx_type)
    if category and category != "Все":
        query = query.filter(models.Transaction.category == category)
    if year:
        query = query.filter(models.Transaction.date >= date(year, 1, 1))
        query = query.filter(models.Transaction.date <= date(year, 12, 31))
    if month:
        query = query.filter(models.Transaction.date.month == month)
        
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }

@router.post("/", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_transaction = models.Transaction(
        **transaction.model_dump(),  # Pydantic v2: используем model_dump() вместо dict()
        user_id=current_user.id  # 🔐 АВТО-ПРИВЯЗКА К ПОЛЬЗОВАТЕЛЮ
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.delete("/{tx_id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    tx = db.query(models.Transaction).filter(
        models.Transaction.id == tx_id,
        models.Transaction.user_id == current_user.id  # 🔐 ПРОВЕРКА ВЛАДЕНИЯ
    ).first()
    
    if not tx:
        raise HTTPException(status_code=404, detail="Транзакция не найдена или нет прав")
        
    db.delete(tx)
    db.commit()
    return {"detail": "Транзакция удалена"}
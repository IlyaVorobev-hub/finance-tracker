# src/api/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from typing import List, Optional
from typing import Optional
from datetime import date
from .. import models, schemas, database, auth


router = APIRouter(tags=["transactions"])

@router.get("/summary", response_model=dict)
def get_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    category: Optional[str] = Query(None),  # ✅ Должно быть!
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    q = db.query(
        func.sum(case((models.Transaction.type == 'income', models.Transaction.amount))).label('income'),
        func.sum(case((models.Transaction.type == 'expense', models.Transaction.amount))).label('expense')
    ).filter(models.Transaction.user_id == current_user.id)
    
    if year: q = q.filter(extract('year', models.Transaction.date) == year)
    if month and year: q = q.filter(extract('month', models.Transaction.date) == month)
    if category: q = q.filter(models.Transaction.category == category)  # ✅ Фильтр по категории!
    
    r = q.first()
    inc, exp = r.income or 0, r.expense or 0
    return {"total_income": inc, "total_expense": exp, "balance": inc - exp}

@router.get("/", response_model=List[schemas.TransactionResponse])
def list_transactions(
    skip: int = 0, limit: int = 100,
    type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    category: Optional[str] = Query(None),  # 👈 Новый фильтр
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    if type: q = q.filter(models.Transaction.type == type)
    if year: q = q.filter(extract('year', models.Transaction.date) == year)
    if month and year: q = q.filter(extract('month', models.Transaction.date) == month)
    if category: q = q.filter(models.Transaction.category == category)  # 👈 Применяем фильтр
    return q.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.TransactionResponse, status_code=201)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_tx = models.Transaction(**tx.model_dump(), user_id=current_user.id)
    db.add(db_tx); db.commit(); db.refresh(db_tx)
    return db_tx

@router.delete("/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id, models.Transaction.user_id == current_user.id).first()
    if not tx: raise HTTPException(404, "Not found")
    db.delete(tx); db.commit()
    return {"status": "deleted"}
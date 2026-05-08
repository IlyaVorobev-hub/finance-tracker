# src/api/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# ✅ Абсолютные импорты
from src.api import models, schemas, database
from src.api.auth import get_current_user
from src.api.limiter import limiter

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[schemas.TransactionOut])
@limiter.limit("30/minute")
async def get_transactions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[schemas.TransactionType] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить список транзакций пользователя"""
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    )
    
    # Фильтры
    if type:
        query = query.filter(models.Transaction.type == type)
    if category:
        query = query.join(models.Category).filter(
            models.Category.name.ilike(f"%{category}%")
        )
    if date_from:
        query = query.filter(models.Transaction.date >= date_from)
    if date_to:
        query = query.filter(models.Transaction.date <= date_to)
    
    transactions = query.offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
@limiter.limit("30/minute")
async def get_transaction(
    request: Request,
    transaction_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить одну транзакцию по ID"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction


@router.post("/", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_transaction(
    request: Request,
    transaction_in: schemas.TransactionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Создать новую транзакцию"""
    # 🔧 Обработка category как строки (название)
    category = None
    if transaction_in.category:
        # Ищем категорию по названию
        category = db.query(models.Category).filter(
            models.Category.name == transaction_in.category,
            models.Category.type == transaction_in.type
        ).first()
        
        # Если не найдена — создаём новую
        if not category:
            category = models.Category(
                name=transaction_in.category,
                type=transaction_in.type,
                user_id=current_user.id
            )
            db.add(category)
            db.commit()
            db.refresh(category)
    
    # Создаём транзакцию
    transaction = models.Transaction(
        amount=transaction_in.amount,
        description=transaction_in.description,
        date=transaction_in.date,
        type=transaction_in.type,
        payment_method=transaction_in.payment_method,
        user_id=current_user.id,
        category_id=category.id if category else None
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.put("/{transaction_id}", response_model=schemas.TransactionOut)
@limiter.limit("20/minute")
async def update_transaction(
    request: Request,
    transaction_id: int,
    transaction_in: schemas.TransactionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Обновить транзакцию"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Обновляем поля
    for field, value in transaction_in.model_dump(exclude_unset=True).items():
        if field == "category":
            # Обработка категории
            if value:
                category = db.query(models.Category).filter(
                    models.Category.name == value,
                    models.Category.type == transaction_in.type
                ).first()
                if not category:
                    category = models.Category(
                        name=value,
                        type=transaction_in.type,
                        user_id=current_user.id
                    )
                    db.add(category)
                    db.commit()
                    db.refresh(category)
                transaction.category_id = category.id
        elif field not in ["category", "category_id"]:
            setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Удалить транзакцию"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    return None
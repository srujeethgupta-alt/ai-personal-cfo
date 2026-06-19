from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from models import Expense, User
from schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from services.analytics_service import get_total_expenses
from auth import get_current_user

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_expense = Expense(
        user_id=current_user.id,
        category=expense.category,
        amount=expense.amount,
        expense_date=expense.expense_date,
        notes=expense.notes
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"success": True, "message": "Expense added successfully", "id": new_expense.id}


@router.get("", response_model=dict)
def get_expenses(
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Expense).filter(Expense.is_deleted == False, Expense.user_id == current_user.id)
    if category:
        query = query.filter(Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    
    total = query.count()
    expenses = query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()
    data = [
        {
            "id": e.id,
            "user_id": e.user_id,
            "category": e.category,
            "amount": float(e.amount),
            "expense_date": e.expense_date.isoformat() if e.expense_date else None,
            "notes": e.notes,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in expenses
    ]
    return {"success": True, "data": data, "total": total, "skip": skip, "limit": limit}


@router.get("/summary", response_model=dict)
def expense_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = get_total_expenses(db, user_id=current_user.id)
    category_rows = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.is_deleted == False,
        Expense.user_id == current_user.id
    ).group_by(Expense.category).all()
    
    return {
        "success": True,
        "data": {
            "total_expenses": total,
            "category_breakdown": {cat: float(amt) for cat, amt in category_rows}
        }
    }


@router.put("/{expense_id}", response_model=dict)
def update_expense(expense_id: int, expense_update: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense_update.category is not None:
        expense.category = expense_update.category
    if expense_update.amount is not None:
        expense.amount = expense_update.amount
    if expense_update.expense_date is not None:
        expense.expense_date = expense_update.expense_date
    if expense_update.notes is not None:
        expense.notes = expense_update.notes
    
    db.commit()
    db.refresh(expense)
    return {"success": True, "message": "Expense updated successfully"}


@router.delete("/{expense_id}", response_model=dict)
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.is_deleted = True
    expense.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Expense deleted successfully"}

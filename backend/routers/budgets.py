from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Budget, Expense, User
from schemas import BudgetCreate, BudgetResponse
from services.analytics_service import get_budget_status
from auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_budget(budget: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if budget for this category/month/year already exists
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == budget.category,
        Budget.month == budget.month,
        Budget.year == budget.year,
        Budget.is_deleted == False
    ).first()
    
    if existing:
        existing.budget_amount = budget.budget_amount
        db.commit()
        db.refresh(existing)
        return {"success": True, "message": "Budget updated successfully", "id": existing.id}
    
    new_budget = Budget(
        user_id=current_user.id,
        category=budget.category,
        budget_amount=budget.budget_amount,
        month=budget.month,
        year=budget.year
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return {"success": True, "message": "Budget added successfully", "id": new_budget.id}


@router.get("", response_model=dict)
def get_budgets(
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    query = db.query(Budget).filter(
        Budget.month == month,
        Budget.year == year,
        Budget.is_deleted == False,
        Budget.user_id == current_user.id
    )
    total = query.count()
    budgets = query.offset(skip).limit(limit).all()
    
    data = [
        {
            "id": b.id,
            "user_id": b.user_id,
            "category": b.category,
            "budget_amount": float(b.budget_amount),
            "month": b.month,
            "year": b.year,
            "created_at": b.created_at.isoformat() if b.created_at else None
        }
        for b in budgets
    ]
    return {"success": True, "data": data, "total": total, "skip": skip, "limit": limit}


@router.get("/status", response_model=dict)
def budget_status(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = get_budget_status(db, user_id=current_user.id, month=month, year=year)
    return {"success": True, "data": data}


@router.delete("/{budget_id}", response_model=dict)
def delete_budget(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.is_deleted == False, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.is_deleted = True
    budget.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Budget deleted successfully"}

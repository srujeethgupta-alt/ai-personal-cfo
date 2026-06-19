from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from models import Investment, User
from schemas import InvestmentCreate, InvestmentResponse, InvestmentUpdate
from services.analytics_service import get_total_invested, get_total_investments
from auth import get_current_user

router = APIRouter(prefix="/api/investments", tags=["investments"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_investment(investment: InvestmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_investment = Investment(
        user_id=current_user.id,
        investment_type=investment.investment_type,
        investment_name=investment.investment_name,
        amount_invested=investment.amount_invested,
        current_value=investment.current_value,
        start_date=investment.start_date,
        maturity_date=investment.maturity_date,
        status=investment.status
    )
    db.add(new_investment)
    db.commit()
    db.refresh(new_investment)
    return {"success": True, "message": "Investment added successfully", "id": new_investment.id}


@router.get("", response_model=dict)
def get_investments(
    type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Investment).filter(Investment.is_deleted == False, Investment.user_id == current_user.id)
    if type:
        query = query.filter(Investment.investment_type.ilike(f"%{type}%"))
    if status:
        query = query.filter(Investment.status.ilike(f"%{status}%"))
    
    total = query.count()
    investments = query.order_by(Investment.created_at.desc()).offset(skip).limit(limit).all()
    data = [
        {
            "id": inv.id,
            "user_id": inv.user_id,
            "investment_type": inv.investment_type,
            "investment_name": inv.investment_name,
            "amount_invested": float(inv.amount_invested),
            "current_value": float(inv.current_value),
            "profit_loss": inv.profit_loss,
            "roi": round(inv.roi, 2),
            "status": inv.status,
            "start_date": inv.start_date.isoformat() if inv.start_date else None,
            "maturity_date": inv.maturity_date.isoformat() if inv.maturity_date else None,
            "created_at": inv.created_at.isoformat() if inv.created_at else None
        }
        for inv in investments
    ]
    return {"success": True, "data": data, "total": total, "skip": skip, "limit": limit}


@router.get("/summary", response_model=dict)
def investment_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_invested = get_total_invested(db, user_id=current_user.id)
    current_value = get_total_investments(db, user_id=current_user.id)
    profit = current_value - total_invested
    roi = 0.0
    if total_invested > 0:
        roi = (profit / total_invested) * 100
    
    return {
        "success": True,
        "data": {
            "total_invested": total_invested,
            "current_value": current_value,
            "profit": round(profit, 2),
            "roi": round(roi, 2)
        }
    }


@router.put("/{investment_id}", response_model=dict)
def update_investment(investment_id: int, investment_update: InvestmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.is_deleted == False, Investment.user_id == current_user.id).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    if investment_update.investment_type is not None:
        investment.investment_type = investment_update.investment_type
    if investment_update.investment_name is not None:
        investment.investment_name = investment_update.investment_name
    if investment_update.amount_invested is not None:
        investment.amount_invested = investment_update.amount_invested
    if investment_update.current_value is not None:
        investment.current_value = investment_update.current_value
    if investment_update.start_date is not None:
        investment.start_date = investment_update.start_date
    if investment_update.maturity_date is not None:
        investment.maturity_date = investment_update.maturity_date
    if investment_update.status is not None:
        investment.status = investment_update.status
    
    db.commit()
    db.refresh(investment)
    return {"success": True, "message": "Investment updated successfully"}


@router.delete("/{investment_id}", response_model=dict)
def delete_investment(investment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.is_deleted == False, Investment.user_id == current_user.id).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    investment.is_deleted = True
    investment.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Investment deleted successfully"}

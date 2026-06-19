from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from models import Loan, User
from schemas import LoanCreate, LoanResponse, LoanUpdate
from services.analytics_service import get_total_loans, get_total_emi, get_loan_summary
from auth import get_current_user

router = APIRouter(prefix="/api/loans", tags=["loans"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_loan(loan: LoanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_loan = Loan(
        user_id=current_user.id,
        loan_name=loan.loan_name,
        principal_amount=loan.principal_amount,
        remaining_amount=loan.remaining_amount,
        interest_rate=loan.interest_rate,
        emi=loan.emi,
        start_date=loan.start_date,
        end_date=loan.end_date,
        status=loan.status
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return {"success": True, "message": "Loan added successfully", "id": new_loan.id}


@router.get("", response_model=dict)
def get_loans(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Loan).filter(Loan.is_deleted == False, Loan.user_id == current_user.id)
    if status:
        query = query.filter(Loan.status.ilike(f"%{status}%"))
    
    total = query.count()
    loans = query.order_by(Loan.created_at.desc()).offset(skip).limit(limit).all()
    data = [
        {
            "id": loan.id,
            "user_id": loan.user_id,
            "loan_name": loan.loan_name,
            "principal_amount": float(loan.principal_amount),
            "remaining_amount": float(loan.remaining_amount),
            "interest_rate": loan.interest_rate,
            "emi": float(loan.emi),
            "status": loan.status,
            "start_date": loan.start_date.isoformat() if loan.start_date else None,
            "end_date": loan.end_date.isoformat() if loan.end_date else None,
            "created_at": loan.created_at.isoformat() if loan.created_at else None,
            "months_remaining": loan.months_remaining,
            "total_interest_payable": round(loan.total_interest_payable, 2)
        }
        for loan in loans
    ]
    return {"success": True, "data": data, "total": total, "skip": skip, "limit": limit}


@router.get("/summary", response_model=dict)
def loan_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = get_loan_summary(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.put("/{loan_id}", response_model=dict)
def update_loan(loan_id: int, loan_update: LoanUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.is_deleted == False, Loan.user_id == current_user.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan_update.loan_name is not None:
        loan.loan_name = loan_update.loan_name
    if loan_update.principal_amount is not None:
        loan.principal_amount = loan_update.principal_amount
    if loan_update.remaining_amount is not None:
        loan.remaining_amount = loan_update.remaining_amount
    if loan_update.interest_rate is not None:
        loan.interest_rate = loan_update.interest_rate
    if loan_update.emi is not None:
        loan.emi = loan_update.emi
    if loan_update.start_date is not None:
        loan.start_date = loan_update.start_date
    if loan_update.end_date is not None:
        loan.end_date = loan_update.end_date
    if loan_update.status is not None:
        loan.status = loan_update.status
    
    db.commit()
    db.refresh(loan)
    return {"success": True, "message": "Loan updated successfully"}


@router.delete("/{loan_id}", response_model=dict)
def delete_loan(loan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.is_deleted == False, Loan.user_id == current_user.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    loan.is_deleted = True
    loan.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Loan deleted successfully"}

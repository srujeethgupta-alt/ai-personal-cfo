from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


def require_admin(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "country": current_user.country,
            "currency": current_user.currency,
            "salary": float(current_user.salary) if current_user.salary else 0.0,
            "occupation": current_user.occupation,
            "risk_profile": current_user.risk_profile,
            "onboarding_complete": current_user.onboarding_complete,
            "is_admin": getattr(current_user, "is_admin", False)
        }
    }


@router.put("/me", response_model=dict)
def update_me(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = ["name", "country", "currency", "salary", "occupation", "risk_profile"]
    for field in allowed:
        if field in data:
            setattr(current_user, field, data[field])
    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "Profile updated"}


@router.get("", response_model=dict, dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).all()
    data = [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "is_admin": getattr(u, "is_admin", False),
            "onboarding_complete": u.onboarding_complete
        }
        for u in users
    ]
    return {"success": True, "data": data}


@router.delete("/{user_id}", response_model=dict, dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    user.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "User deactivated"}

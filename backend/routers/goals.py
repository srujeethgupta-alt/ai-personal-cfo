from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from models import Goal, User
from schemas import GoalCreate, GoalResponse, GoalUpdate
from services.analytics_service import get_goal_progress
from auth import get_current_user

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_goal = Goal(
        user_id=current_user.id,
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        status=goal.status
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return {"success": True, "message": "Goal added successfully", "id": new_goal.id}


@router.get("", response_model=dict)
def get_goals(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Goal).filter(Goal.is_deleted == False, Goal.user_id == current_user.id)
    if status:
        query = query.filter(Goal.status.ilike(f"%{status}%"))
    
    total = query.count()
    goals = query.order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()
    data = [
        {
            "id": g.id,
            "user_id": g.user_id,
            "goal_name": g.goal_name,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "remaining": g.remaining,
            "progress": round(g.progress, 2),
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "status": g.status,
            "created_at": g.created_at.isoformat() if g.created_at else None
        }
        for g in goals
    ]
    return {"success": True, "data": data, "total": total, "skip": skip, "limit": limit}


@router.get("/summary", response_model=dict)
def goal_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goals = db.query(Goal).filter(Goal.is_deleted == False, Goal.user_id == current_user.id).all()
    total_target = sum(float(g.target_amount) for g in goals)
    total_saved = sum(float(g.current_amount) for g in goals)
    progress = 0.0
    if total_target > 0:
        progress = (total_saved / total_target) * 100
    
    active = sum(1 for g in goals if g.status == "Active")
    completed = sum(1 for g in goals if g.status == "Completed")
    
    return {
        "success": True,
        "data": {
            "total_target": total_target,
            "total_saved": total_saved,
            "progress": round(progress, 2),
            "active_goals": active,
            "completed_goals": completed
        }
    }


@router.put("/{goal_id}", response_model=dict)
def update_goal(goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.is_deleted == False, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal_update.goal_name is not None:
        goal.goal_name = goal_update.goal_name
    if goal_update.target_amount is not None:
        goal.target_amount = goal_update.target_amount
    if goal_update.current_amount is not None:
        goal.current_amount = goal_update.current_amount
    if goal_update.target_date is not None:
        goal.target_date = goal_update.target_date
    if goal_update.status is not None:
        goal.status = goal_update.status
    
    db.commit()
    db.refresh(goal)
    return {"success": True, "message": "Goal updated successfully"}


@router.delete("/{goal_id}", response_model=dict)
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.is_deleted == False, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal.is_deleted = True
    goal.deleted_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Goal deleted successfully"}

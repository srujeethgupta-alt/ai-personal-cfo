from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from database import get_db
from models import User, Expense, Investment, Loan, Goal, Budget
from auth import get_current_user
from services.analytics_service import (
    get_dashboard_data, get_health_score, get_net_worth,
    get_cash_flow, get_ai_insights, get_goal_progress,
    get_forecast, get_budget_status, get_or_create_user,
    build_ai_context, get_expense_category_breakdown,
    get_monthly_expense_trends, get_investment_allocation,
    get_loan_summary, get_total_expenses, get_total_investments,
    get_total_loans, get_total_emi, get_user_salary
)
from services.ai_service import ask_ai, ask_ai_streaming
from fastapi.responses import StreamingResponse

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=dict)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Consolidated dashboard data."""
    data = get_dashboard_data(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/health-score", response_model=dict)
def health_score(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Financial health score with rating and suggestions."""
    data = get_health_score(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/net-worth", response_model=dict)
def net_worth(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Net worth with asset and liability breakdowns."""
    data = get_net_worth(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/cash-flow", response_model=dict)
def cash_flow(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Monthly cash flow analysis."""
    data = get_cash_flow(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/ai-insights", response_model=dict)
def ai_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Rule-based financial insights."""
    data = get_ai_insights(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/goal-progress", response_model=dict)
def goal_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Goal progress with time-to-goal estimates."""
    data = get_goal_progress(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/forecast", response_model=dict)
def forecast(months: int = 12, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Financial forecast for next N months."""
    data = get_forecast(db, user_id=current_user.id, months=months)
    return {"success": True, "data": data}


@router.get("/expense-chart", response_model=dict)
def expense_chart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Category-wise expense breakdown for charts."""
    data = get_expense_category_breakdown(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/expense-trends", response_model=dict)
def expense_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Monthly expense trends."""
    data = get_monthly_expense_trends(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/investment-allocation", response_model=dict)
def investment_allocation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Investment type allocation."""
    data = get_investment_allocation(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/loan-summary", response_model=dict)
def loan_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Comprehensive loan summary."""
    data = get_loan_summary(db, user_id=current_user.id)
    return {"success": True, "data": data}


@router.get("/budget-status", response_model=dict)
def budget_status(month: Optional[int] = None, year: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Budget vs actual spending comparison."""
    data = get_budget_status(db, user_id=current_user.id, month=month, year=year)
    return {"success": True, "data": data}

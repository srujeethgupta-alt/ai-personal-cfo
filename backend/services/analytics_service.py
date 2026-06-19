# services/analytics_service.py
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, date
from collections import defaultdict

from models import User, Expense, Investment, Loan, Goal, Budget

logger = logging.getLogger(__name__)


def get_or_create_user(db: Session, user_id: int = 1) -> Optional[User]:
    """Get user by ID, or create a default user if none exists."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        # Create default user if none exists
        user = User(id=1, name="Default User", salary=0.0, currency="INR")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user_salary(db: Session, user_id: int = 1) -> float:
    """Safely get user salary with fallback to 0."""
    user = get_or_create_user(db, user_id)
    return float(user.salary) if user and user.salary else 0.0


def get_total_expenses(db: Session, user_id: int = 1) -> float:
    """Sum of all non-deleted expenses for user."""
    result = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.is_deleted == False
    ).scalar()
    return float(result) if result else 0.0


def get_expense_category_breakdown(db: Session, user_id: int = 1) -> Dict[str, float]:
    """Category-wise expense breakdown."""
    rows = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.is_deleted == False
    ).group_by(Expense.category).all()
    return {cat: float(amt) for cat, amt in rows}


def get_monthly_expense_trends(db: Session, user_id: int = 1, months: int = 6) -> Dict[str, float]:
    """Monthly expense totals for last N months."""
    rows = db.query(
        extract('year', Expense.expense_date).label('year'),
        extract('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == user_id,
        Expense.is_deleted == False
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    trends = {}
    for r in rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        trends[key] = float(r.total)
    return trends


def get_total_investments(db: Session, user_id: int = 1) -> float:
    """Sum of current values of all non-deleted investments."""
    result = db.query(func.sum(Investment.current_value)).filter(
        Investment.user_id == user_id,
        Investment.is_deleted == False
    ).scalar()
    return float(result) if result else 0.0


def get_total_invested(db: Session, user_id: int = 1) -> float:
    """Sum of amount invested."""
    result = db.query(func.sum(Investment.amount_invested)).filter(
        Investment.user_id == user_id,
        Investment.is_deleted == False
    ).scalar()
    return float(result) if result else 0.0


def get_investment_allocation(db: Session, user_id: int = 1) -> Dict[str, float]:
    """Investment type allocation."""
    rows = db.query(Investment.investment_type, func.sum(Investment.current_value)).filter(
        Investment.user_id == user_id,
        Investment.is_deleted == False
    ).group_by(Investment.investment_type).all()
    return {t: float(v) for t, v in rows}


def get_total_loans(db: Session, user_id: int = 1) -> float:
    """Sum of remaining loan amounts."""
    result = db.query(func.sum(Loan.remaining_amount)).filter(
        Loan.user_id == user_id,
        Loan.is_deleted == False
    ).scalar()
    return float(result) if result else 0.0


def get_total_emi(db: Session, user_id: int = 1) -> float:
    """Sum of monthly EMIs."""
    result = db.query(func.sum(Loan.emi)).filter(
        Loan.user_id == user_id,
        Loan.is_deleted == False,
        Loan.status == "Active"
    ).scalar()
    return float(result) if result else 0.0


def get_loan_summary(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Comprehensive loan summary."""
    total_loan = get_total_loans(db, user_id)
    total_emi = get_total_emi(db, user_id)
    salary = get_user_salary(db, user_id)
    
    debt_burden = 0.0
    if salary > 0:
        debt_burden = (total_emi / salary) * 100
    
    payoff_months = 0
    if total_emi > 0:
        payoff_months = int(total_loan / total_emi)
    
    return {
        "total_loan": total_loan,
        "total_emi": total_emi,
        "debt_burden_ratio": round(debt_burden, 2),
        "payoff_projection_months": payoff_months
    }


def get_net_worth(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Calculate net worth with breakdowns."""
    assets = get_total_investments(db, user_id)
    liabilities = get_total_loans(db, user_id)
    
    asset_breakdown = get_investment_allocation(db, user_id)
    liability_breakdown = {}
    
    loans = db.query(Loan).filter(Loan.user_id == user_id, Loan.is_deleted == False).all()
    for loan in loans:
        liability_breakdown[loan.loan_name] = float(loan.remaining_amount)
    
    return {
        "total_assets": assets,
        "total_liabilities": liabilities,
        "net_worth": assets - liabilities,
        "asset_breakdown": asset_breakdown,
        "liability_breakdown": liability_breakdown
    }


def get_cash_flow(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Monthly cash flow analysis."""
    salary = get_user_salary(db, user_id)
    expenses = get_total_expenses(db, user_id)
    emi = get_total_emi(db, user_id)
    
    # If expenses are stored for a period, approximate monthly
    # For now, assume expenses are monthly total
    monthly_expenses = expenses
    monthly_savings = salary - monthly_expenses
    free_cash_flow = monthly_savings - emi
    
    savings_rate = 0.0
    if salary > 0:
        savings_rate = (monthly_savings / salary) * 100
    
    return {
        "monthly_income": salary,
        "monthly_expenses": monthly_expenses,
        "monthly_savings": monthly_savings,
        "monthly_emi": emi,
        "free_cash_flow": free_cash_flow,
        "savings_rate": round(savings_rate, 2)
    }


def get_health_score(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Calculate financial health score with rating."""
    salary = get_user_salary(db, user_id)
    expenses = get_total_expenses(db, user_id)
    savings = salary - expenses
    
    score = 0.0
    if salary > 0:
        score = (savings / salary) * 100
    
    # Clamp to 0-100
    score = max(0, min(100, score))
    
    if score >= 50:
        rating = "Excellent"
    elif score >= 30:
        rating = "Good"
    elif score >= 15:
        rating = "Fair"
    elif score > 0:
        rating = "Poor"
    else:
        rating = "Critical"
    
    suggestions = []
    if score < 20:
        suggestions.append("Your savings rate is very low. Try to reduce discretionary spending.")
    if score > 50:
        suggestions.append("Great savings rate! Consider investing surplus for long-term growth.")
    
    return {
        "salary": salary,
        "expenses": expenses,
        "savings": savings,
        "health_score": round(score, 2),
        "rating": rating,
        "suggestions": suggestions
    }


def get_ai_insights(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Generate rule-based financial insights."""
    insights = []
    severity = "good"
    
    salary = get_user_salary(db, user_id)
    expenses = get_total_expenses(db, user_id)
    investments = get_total_investments(db, user_id)
    loans = get_total_loans(db, user_id)
    emi = get_total_emi(db, user_id)
    
    if salary > 0:
        if expenses > salary * 0.7:
            insights.append("Expenses exceed 70% of your salary. Consider cutting non-essential spending.")
            severity = "warning"
        if expenses > salary:
            insights.append("You are spending more than you earn. Immediate budget review is needed.")
            severity = "critical"
        if emi > salary * 0.4:
            insights.append("EMI burden exceeds 40% of income. This is a high-risk zone.")
            severity = "critical"
        if investments < salary * 0.1:
            insights.append("Investment allocation is low. Aim for at least 10-20% of income in investments.")
            if severity == "good":
                severity = "warning"
        if loans > investments * 2:
            insights.append("Debt is significantly higher than investments. Focus on debt reduction.")
            if severity == "good":
                severity = "warning"
    
    if not insights:
        insights.append("Your financial health looks stable. Keep monitoring your progress.")
    
    return {
        "insights": insights,
        "severity": severity
    }


def get_goal_progress(db: Session, user_id: int = 1) -> List[Dict[str, Any]]:
    """Get goal progress with projections."""
    goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.is_deleted == False).all()
    result = []
    
    for goal in goals:
        progress = goal.progress
        remaining = goal.remaining
        
        # Estimate months to goal based on current savings rate
        salary = get_user_salary(db, user_id)
        expenses = get_total_expenses(db, user_id)
        monthly_savings = salary - expenses
        
        months_to_goal = None
        if monthly_savings > 0 and remaining > 0:
            months_to_goal = int(remaining / monthly_savings)
        elif remaining <= 0:
            months_to_goal = 0
        else:
            months_to_goal = float('inf')
        
        result.append({
            "goal": goal.goal_name,
            "target": float(goal.target_amount),
            "current": float(goal.current_amount),
            "remaining": remaining,
            "progress": round(progress, 2),
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "months_to_goal": months_to_goal if months_to_goal != float('inf') else None,
            "status": goal.status
        })
    
    return result


def get_forecast(db: Session, user_id: int = 1, months: int = 12) -> Dict[str, Any]:
    """Project financial forecast."""
    salary = get_user_salary(db, user_id)
    expenses = get_total_expenses(db, user_id)
    monthly_savings = salary - expenses
    
    net_worth_now = get_net_worth(db, user_id)["net_worth"]
    
    month_labels = []
    projected_savings = []
    projected_net_worth = []
    projected_goals = []
    
    for i in range(1, months + 1):
        month_labels.append(f"Month {i}")
        cumulative_savings = monthly_savings * i
        projected_savings.append(round(cumulative_savings, 2))
        projected_net_worth.append(round(net_worth_now + cumulative_savings, 2))
    
    # Goal projections
    goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.is_deleted == False).all()
    for goal in goals:
        remaining = goal.remaining
        if monthly_savings > 0 and remaining > 0:
            months_needed = int(remaining / monthly_savings)
            projected_goals.append({
                "goal": goal.goal_name,
                "months_to_achieve": months_needed,
                "achievable": months_needed <= months
            })
    
    return {
        "months": month_labels,
        "projected_savings": projected_savings,
        "projected_net_worth": projected_net_worth,
        "projected_goals": projected_goals
    }


def get_budget_status(db: Session, user_id: int = 1, month: int = None, year: int = None) -> List[Dict[str, Any]]:
    """Compare budget vs actual spending by category."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == month,
        Budget.year == year,
        Budget.is_deleted == False
    ).all()
    
    # Get actual spending for this month
    actual_spending = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.is_deleted == False,
        extract('month', Expense.expense_date) == month,
        extract('year', Expense.expense_date) == year
    ).group_by(Expense.category).all()
    
    actual_map = {cat: float(amt) for cat, amt in actual_spending}
    
    result = []
    for b in budgets:
        spent = actual_map.get(b.category, 0.0)
        budgeted = float(b.budget_amount)
        remaining = budgeted - spent
        utilization = (spent / budgeted * 100) if budgeted > 0 else 0.0
        
        result.append({
            "category": b.category,
            "budgeted": budgeted,
            "spent": spent,
            "remaining": round(remaining, 2),
            "utilization_pct": round(utilization, 2)
        })
    
    return result


def get_dashboard_data(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Consolidated dashboard data."""
    salary = get_user_salary(db, user_id)
    expenses = get_total_expenses(db, user_id)
    investments = get_total_investments(db, user_id)
    loans = get_total_loans(db, user_id)
    net_worth = investments - loans
    
    health = get_health_score(db, user_id)
    cash_flow = get_cash_flow(db, user_id)
    
    debt_to_income = 0.0
    if salary > 0:
        debt_to_income = (loans / salary) * 100
    
    investment_coverage = 0.0
    if loans > 0:
        investment_coverage = (investments / loans) * 100
    
    return {
        "salary": salary,
        "expenses": expenses,
        "investments": investments,
        "loans": loans,
        "net_worth": net_worth,
        "health_score": health["health_score"],
        "goal_progress": get_goal_progress(db, user_id),
        "savings_rate": cash_flow["savings_rate"],
        "debt_to_income": round(debt_to_income, 2),
        "investment_coverage": round(investment_coverage, 2)
    }


def build_ai_context(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """Build a comprehensive financial context for AI prompts."""
    user = get_or_create_user(db, user_id)
    
    return {
        "user_name": user.name if user else "User",
        "currency": user.currency if user else "INR",
        "salary": get_user_salary(db, user_id),
        "total_expenses": get_total_expenses(db, user_id),
        "expense_categories": get_expense_category_breakdown(db, user_id),
        "monthly_trends": get_monthly_expense_trends(db, user_id),
        "total_investments": get_total_investments(db, user_id),
        "total_invested": get_total_invested(db, user_id),
        "investment_allocation": get_investment_allocation(db, user_id),
        "total_loans": get_total_loans(db, user_id),
        "total_emi": get_total_emi(db, user_id),
        "net_worth": get_net_worth(db, user_id),
        "cash_flow": get_cash_flow(db, user_id),
        "health_score": get_health_score(db, user_id),
        "goals": get_goal_progress(db, user_id),
        "insights": get_ai_insights(db, user_id),
        "forecast": get_forecast(db, user_id, months=6)
    }

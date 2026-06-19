from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Expense, Investment, Loan, Goal, Budget, User


def _parse_date(value: Any) -> Optional[date]:
    """Parse a string or date value into a date object."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        # Try ISO format (YYYY-MM-DD)
        try:
            return date.fromisoformat(value)
        except ValueError:
            # Try common formats
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
    return None


def _to_dict(obj, extra: Optional[dict] = None) -> dict:
    """Convert a SQLAlchemy model instance to a plain dict."""
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, Decimal):
            result[col.name] = float(val)
        elif isinstance(val, (date, datetime)):
            result[col.name] = val.isoformat()
        else:
            result[col.name] = val
    if extra:
        result.update(extra)
    return result


def _verify_ownership(db: Session, model, record_id: int, user_id: int):
    """Verify a record exists and belongs to the user. Returns the record or None."""
    record = db.query(model).filter(
        model.id == record_id,
        model.user_id == user_id,
        model.is_deleted == False
    ).first()
    return record


def create_expense(db: Session, user_id: int, category: str, amount: float, expense_date: Any, notes: Optional[str] = None):
    try:
        parsed_date = _parse_date(expense_date)
        if not parsed_date:
            return {"success": False, "message": "Invalid expense_date format. Use YYYY-MM-DD.", "data": None}

        expense = Expense(
            user_id=user_id,
            category=category,
            amount=amount,
            expense_date=parsed_date,
            notes=notes
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return {"success": True, "message": "Expense created successfully", "data": _to_dict(expense)}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to create expense: {str(e)}", "data": None}


def update_expense(db: Session, expense_id: int, user_id: int, **kwargs):
    try:
        expense = _verify_ownership(db, Expense, expense_id, user_id)
        if not expense:
            return {"success": False, "message": "Expense not found or access denied", "data": None}

        allowed_fields = {"category", "amount", "expense_date", "notes"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == "expense_date":
                    parsed = _parse_date(value)
                    if parsed:
                        setattr(expense, key, parsed)
                else:
                    setattr(expense, key, value)

        db.commit()
        db.refresh(expense)
        return {"success": True, "message": "Expense updated successfully", "data": _to_dict(expense)}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to update expense: {str(e)}", "data": None}


def delete_expense(db: Session, expense_id: int, user_id: int):
    try:
        expense = _verify_ownership(db, Expense, expense_id, user_id)
        if not expense:
            return {"success": False, "message": "Expense not found or access denied", "data": None}

        expense.is_deleted = True
        expense.deleted_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Expense deleted successfully", "data": {"id": expense_id}}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to delete expense: {str(e)}", "data": None}


def create_goal(db: Session, user_id: int, goal_name: str, target_amount: float, current_amount: float = 0.0, target_date: Any = None):
    try:
        parsed_date = _parse_date(target_date)
        goal = Goal(
            user_id=user_id,
            goal_name=goal_name,
            target_amount=target_amount,
            current_amount=current_amount or 0.0,
            target_date=parsed_date,
            status="Active"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return {
            "success": True,
            "message": "Goal created successfully",
            "data": _to_dict(goal, extra={"progress": goal.progress, "remaining": goal.remaining})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to create goal: {str(e)}", "data": None}


def update_goal(db: Session, goal_id: int, user_id: int, **kwargs):
    try:
        goal = _verify_ownership(db, Goal, goal_id, user_id)
        if not goal:
            return {"success": False, "message": "Goal not found or access denied", "data": None}

        allowed_fields = {"goal_name", "target_amount", "current_amount", "target_date", "status"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == "target_date":
                    parsed = _parse_date(value)
                    if parsed:
                        setattr(goal, key, parsed)
                else:
                    setattr(goal, key, value)

        db.commit()
        db.refresh(goal)
        return {
            "success": True,
            "message": "Goal updated successfully",
            "data": _to_dict(goal, extra={"progress": goal.progress, "remaining": goal.remaining})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to update goal: {str(e)}", "data": None}


def delete_goal(db: Session, goal_id: int, user_id: int):
    try:
        goal = _verify_ownership(db, Goal, goal_id, user_id)
        if not goal:
            return {"success": False, "message": "Goal not found or access denied", "data": None}

        goal.is_deleted = True
        goal.deleted_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Goal deleted successfully", "data": {"id": goal_id}}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to delete goal: {str(e)}", "data": None}


def create_investment(db: Session, user_id: int, investment_type: str, investment_name: str, amount_invested: float, current_value: float, start_date: Any = None, maturity_date: Any = None, status: str = "Active"):
    try:
        parsed_start = _parse_date(start_date)
        parsed_maturity = _parse_date(maturity_date)
        investment = Investment(
            user_id=user_id,
            investment_type=investment_type,
            investment_name=investment_name,
            amount_invested=amount_invested,
            current_value=current_value,
            start_date=parsed_start,
            maturity_date=parsed_maturity,
            status=status
        )
        db.add(investment)
        db.commit()
        db.refresh(investment)
        return {
            "success": True,
            "message": "Investment created successfully",
            "data": _to_dict(investment, extra={"profit_loss": investment.profit_loss, "roi": investment.roi})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to create investment: {str(e)}", "data": None}


def update_investment(db: Session, investment_id: int, user_id: int, **kwargs):
    try:
        investment = _verify_ownership(db, Investment, investment_id, user_id)
        if not investment:
            return {"success": False, "message": "Investment not found or access denied", "data": None}

        allowed_fields = {"investment_type", "investment_name", "amount_invested", "current_value", "start_date", "maturity_date", "status"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key in {"start_date", "maturity_date"}:
                    parsed = _parse_date(value)
                    if parsed:
                        setattr(investment, key, parsed)
                else:
                    setattr(investment, key, value)

        db.commit()
        db.refresh(investment)
        return {
            "success": True,
            "message": "Investment updated successfully",
            "data": _to_dict(investment, extra={"profit_loss": investment.profit_loss, "roi": investment.roi})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to update investment: {str(e)}", "data": None}


def delete_investment(db: Session, investment_id: int, user_id: int):
    try:
        investment = _verify_ownership(db, Investment, investment_id, user_id)
        if not investment:
            return {"success": False, "message": "Investment not found or access denied", "data": None}

        investment.is_deleted = True
        investment.deleted_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Investment deleted successfully", "data": {"id": investment_id}}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to delete investment: {str(e)}", "data": None}


def create_loan(db: Session, user_id: int, loan_name: str, principal_amount: float, remaining_amount: float, interest_rate: float, emi: float, start_date: Any = None, end_date: Any = None, status: str = "Active"):
    try:
        parsed_start = _parse_date(start_date)
        parsed_end = _parse_date(end_date)
        loan = Loan(
            user_id=user_id,
            loan_name=loan_name,
            principal_amount=principal_amount,
            remaining_amount=remaining_amount,
            interest_rate=interest_rate,
            emi=emi,
            start_date=parsed_start,
            end_date=parsed_end,
            status=status
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return {
            "success": True,
            "message": "Loan created successfully",
            "data": _to_dict(loan, extra={"months_remaining": loan.months_remaining, "total_interest_payable": loan.total_interest_payable})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to create loan: {str(e)}", "data": None}


def update_loan(db: Session, loan_id: int, user_id: int, **kwargs):
    try:
        loan = _verify_ownership(db, Loan, loan_id, user_id)
        if not loan:
            return {"success": False, "message": "Loan not found or access denied", "data": None}

        allowed_fields = {"loan_name", "principal_amount", "remaining_amount", "interest_rate", "emi", "start_date", "end_date", "status"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key in {"start_date", "end_date"}:
                    parsed = _parse_date(value)
                    if parsed:
                        setattr(loan, key, parsed)
                else:
                    setattr(loan, key, value)

        db.commit()
        db.refresh(loan)
        return {
            "success": True,
            "message": "Loan updated successfully",
            "data": _to_dict(loan, extra={"months_remaining": loan.months_remaining, "total_interest_payable": loan.total_interest_payable})
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to update loan: {str(e)}", "data": None}


def delete_loan(db: Session, loan_id: int, user_id: int):
    try:
        loan = _verify_ownership(db, Loan, loan_id, user_id)
        if not loan:
            return {"success": False, "message": "Loan not found or access denied", "data": None}

        loan.is_deleted = True
        loan.deleted_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Loan deleted successfully", "data": {"id": loan_id}}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to delete loan: {str(e)}", "data": None}


def create_budget(db: Session, user_id: int, category: str, budget_amount: float, month: int, year: int):
    try:
        # Check if a budget already exists for this category/month/year
        existing = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category,
            Budget.month == month,
            Budget.year == year,
            Budget.is_deleted == False
        ).first()

        if existing:
            # Update existing budget
            existing.budget_amount = budget_amount
            db.commit()
            db.refresh(existing)
            return {"success": True, "message": "Budget updated successfully", "data": _to_dict(existing)}

        budget = Budget(
            user_id=user_id,
            category=category,
            budget_amount=budget_amount,
            month=month,
            year=year
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return {"success": True, "message": "Budget created successfully", "data": _to_dict(budget)}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to create budget: {str(e)}", "data": None}


def update_profile(db: Session, user_id: int, **kwargs):
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            return {"success": False, "message": "User not found", "data": None}

        allowed_fields = {"name", "salary", "currency", "country", "occupation", "risk_profile", "ai_preferences", "ai_memory"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "salary": float(user.salary) if user.salary else 0,
                "currency": user.currency,
                "country": user.country,
                "occupation": user.occupation,
                "risk_profile": user.risk_profile,
                "onboarding_complete": user.onboarding_complete
            }
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Failed to update profile: {str(e)}", "data": None}


def get_financial_summary(db: Session, user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            return {"success": False, "message": "User not found", "data": None}

        # Expenses
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.is_deleted == False
        ).all()
        total_expenses = sum(float(e.amount) for e in expenses)
        expense_categories = {}
        for e in expenses:
            expense_categories[e.category] = expense_categories.get(e.category, 0) + float(e.amount)

        # Investments
        investments = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.is_deleted == False
        ).all()
        total_invested = sum(float(i.amount_invested) for i in investments)
        total_investment_value = sum(float(i.current_value) for i in investments)
        investment_types = {}
        for i in investments:
            investment_types[i.investment_type] = investment_types.get(i.investment_type, 0) + float(i.current_value)

        # Loans
        loans = db.query(Loan).filter(
            Loan.user_id == user_id,
            Loan.is_deleted == False
        ).all()
        total_loan_remaining = sum(float(l.remaining_amount) for l in loans)
        total_emi = sum(float(l.emi) for l in loans)

        # Goals
        goals = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.is_deleted == False
        ).all()
        total_goal_target = sum(float(g.target_amount) for g in goals)
        total_goal_saved = sum(float(g.current_amount) for g in goals)

        # Budgets
        budgets = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.is_deleted == False
        ).all()
        budget_summary = [
            {
                "category": b.category,
                "budget_amount": float(b.budget_amount),
                "month": b.month,
                "year": b.year
            }
            for b in budgets
        ]

        salary = float(user.salary) if user.salary else 0.0
        net_worth = (total_investment_value + salary) - total_loan_remaining

        return {
            "success": True,
            "message": "Financial summary retrieved successfully",
            "data": {
                "user_id": user_id,
                "currency": user.currency,
                "salary": salary,
                "expenses": {
                    "total": total_expenses,
                    "count": len(expenses),
                    "category_breakdown": expense_categories
                },
                "investments": {
                    "total_invested": total_invested,
                    "current_value": total_investment_value,
                    "profit_loss": total_investment_value - total_invested,
                    "count": len(investments),
                    "type_breakdown": investment_types
                },
                "loans": {
                    "total_remaining": total_loan_remaining,
                    "total_emi": total_emi,
                    "count": len(loans)
                },
                "goals": {
                    "total_target": total_goal_target,
                    "total_saved": total_goal_saved,
                    "count": len(goals)
                },
                "budgets": budget_summary,
                "net_worth": net_worth
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to retrieve financial summary: {str(e)}", "data": None}

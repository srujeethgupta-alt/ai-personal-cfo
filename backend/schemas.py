from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ==========================
# BASE RESPONSE
# ==========================
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# ==========================
# USER SCHEMAS
# ==========================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    salary: float = Field(..., ge=0, description="Monthly salary")
    currency: str = Field(default="INR", max_length=10)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    salary: float
    currency: str
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)


# ==========================
# EXPENSE SCHEMAS
# ==========================
class ExpenseCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    expense_date: date
    notes: Optional[str] = Field(None, max_length=500)


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    category: str
    amount: float
    expense_date: date
    notes: Optional[str] = None
    created_at: datetime


class ExpenseUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class ExpenseSummary(BaseModel):
    total_expenses: float
    category_breakdown: dict
    monthly_trends: dict


# ==========================
# INVESTMENT SCHEMAS
# ==========================
class InvestmentCreate(BaseModel):
    investment_type: str = Field(..., min_length=1, max_length=50)
    investment_name: str = Field(..., min_length=1, max_length=100)
    amount_invested: float = Field(..., ge=0)
    current_value: float = Field(..., ge=0)
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    status: str = Field(default="Active", max_length=20)


class InvestmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    investment_type: str
    investment_name: str
    amount_invested: float
    current_value: float
    profit_loss: float
    roi: float
    status: str
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    created_at: datetime


class InvestmentUpdate(BaseModel):
    investment_type: Optional[str] = Field(None, min_length=1, max_length=50)
    investment_name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount_invested: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)


class InvestmentSummary(BaseModel):
    total_invested: float
    current_value: float
    profit: float
    roi: float
    allocation: dict


# ==========================
# LOAN SCHEMAS
# ==========================
class LoanCreate(BaseModel):
    loan_name: str = Field(..., min_length=1, max_length=100)
    principal_amount: float = Field(..., gt=0)
    remaining_amount: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    emi: float = Field(..., gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default="Active", max_length=20)


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    loan_name: str
    principal_amount: float
    remaining_amount: float
    interest_rate: float
    emi: float
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime
    months_remaining: int
    total_interest_payable: float


class LoanUpdate(BaseModel):
    loan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    principal_amount: Optional[float] = Field(None, gt=0)
    remaining_amount: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    emi: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)


class LoanSummary(BaseModel):
    total_loan: float
    total_emi: float
    debt_burden_ratio: float
    payoff_projection_months: int


# ==========================
# GOAL SCHEMAS
# ==========================
class GoalCreate(BaseModel):
    goal_name: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    target_date: Optional[date] = None
    status: str = Field(default="Active", max_length=20)


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    goal_name: str
    target_amount: float
    current_amount: float
    remaining: float
    progress: float
    target_date: Optional[date] = None
    status: str
    created_at: datetime


class GoalUpdate(BaseModel):
    goal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)


class GoalSummary(BaseModel):
    total_target: float
    total_saved: float
    progress: float
    active_goals: int
    completed_goals: int


# ==========================
# BUDGET SCHEMAS
# ==========================
class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    budget_amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    category: str
    budget_amount: float
    month: int
    year: int
    created_at: datetime


class BudgetStatus(BaseModel):
    category: str
    budgeted: float
    spent: float
    remaining: float
    utilization_pct: float


# ==========================
# DASHBOARD SCHEMAS
# ==========================
class DashboardData(BaseModel):
    salary: float
    expenses: float
    investments: float
    loans: float
    net_worth: float
    health_score: float
    goal_progress: List[dict]
    savings_rate: float
    debt_to_income: float
    investment_coverage: float


class FinancialHealthScore(BaseModel):
    salary: float
    expenses: float
    savings: float
    health_score: float
    rating: str
    suggestions: List[str]


# ==========================
# AI SCHEMAS
# ==========================
class CFOQuestion(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    history: List[dict] = Field(default_factory=list)


class CFOAnswer(BaseModel):
    question: str
    answer: str


class AIAdvisorResponse(BaseModel):
    financial_advice: str


class AIInsightsResponse(BaseModel):
    insights: List[str]
    severity: str  # "good", "warning", "critical"


# ==========================
# NET WORTH SCHEMA
# ==========================
class NetWorthResponse(BaseModel):
    total_assets: float
    total_liabilities: float
    net_worth: float
    asset_breakdown: dict
    liability_breakdown: dict


# ==========================
# CASH FLOW SCHEMA
# ==========================
class CashFlowResponse(BaseModel):
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    monthly_emi: float
    free_cash_flow: float
    savings_rate: float


# ==========================
# FORECAST SCHEMA
# ==========================
class ForecastResponse(BaseModel):
    months: List[str]
    projected_savings: List[float]
    projected_net_worth: List[float]
    projected_goals: List[dict]


# ==========================
# AUTH SCHEMAS
# ==========================
class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$", description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)")
    name: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(default="INR", max_length=10)


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class OnboardingData(BaseModel):
    country: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    salary: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    risk_profile: Optional[str] = Field(None, pattern=r"^(conservative|moderate|aggressive)$")
    goals: Optional[List[str]] = Field(default_factory=list)


class OnboardingResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None


class AIAgentMemory(BaseModel):
    preferences: Optional[dict] = None
    memory: Optional[dict] = None


class AIAgentToolCall(BaseModel):
    tool: str
    parameters: dict


class AIAgentAction(BaseModel):
    action: str
    status: str
    data: Optional[dict] = None
    message: str


class NotificationCreate(BaseModel):
    user_id: int
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=500)
    severity: str = Field(default="info", pattern=r"^(info|warning|critical|success)$")


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    type: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime


class NotificationSummary(BaseModel):
    unread_count: int
    notifications: List[dict]

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Numeric, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import declarative_base, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    salary = Column(Numeric(12, 2), default=0.00)
    currency = Column(String(10), default="INR")
    country = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    risk_profile = Column(String(20), default="moderate")  # conservative, moderate, aggressive
    is_verified = Column(Boolean, default=False)
    onboarding_complete = Column(Boolean, default=False)
    reset_token = Column(String(255), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # AI Memory
    ai_preferences = Column(Text, nullable=True)  # JSON string
    ai_memory = Column(Text, nullable=True)  # JSON string

    # Relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="expenses")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    investment_type = Column(String(50), nullable=False, index=True)
    investment_name = Column(String(100), nullable=False)
    amount_invested = Column(Numeric(12, 2), nullable=False)
    current_value = Column(Numeric(12, 2), nullable=False)
    start_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="investments")

    @property
    def profit_loss(self):
        return float(self.current_value) - float(self.amount_invested)

    @property
    def roi(self):
        if float(self.amount_invested) == 0:
            return 0.0
        return ((float(self.current_value) - float(self.amount_invested)) / float(self.amount_invested)) * 100


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_name = Column(String(100), nullable=False)
    principal_amount = Column(Numeric(12, 2), nullable=False)
    remaining_amount = Column(Numeric(12, 2), nullable=False)
    interest_rate = Column(Float, nullable=False)
    emi = Column(Numeric(12, 2), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="loans")

    @property
    def total_interest_payable(self):
        """Simple interest calculation for total interest over loan term"""
        if float(self.principal_amount) <= 0 or self.interest_rate <= 0:
            return 0.0
        # Simple: interest_rate% of principal
        return (float(self.principal_amount) * self.interest_rate) / 100

    @property
    def months_remaining(self):
        """Estimate months remaining based on remaining_amount / emi"""
        if float(self.emi) <= 0:
            return 0
        return int(float(self.remaining_amount) / float(self.emi))


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0.00)
    target_date = Column(Date, nullable=True)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="goals")

    @property
    def progress(self):
        if float(self.target_amount) == 0:
            return 0.0
        return (float(self.current_amount) / float(self.target_amount)) * 100

    @property
    def remaining(self):
        return float(self.target_amount) - float(self.current_amount)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    budget_amount = Column(Numeric(12, 2), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="budgets")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    severity = Column(String(20), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="notifications")

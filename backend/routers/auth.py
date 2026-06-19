from rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse, PasswordResetRequest, PasswordResetConfirm, OnboardingData, OnboardingResponse
from auth import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    decode_token, authenticate_user, get_current_user
)
from services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        name=data.name,
        country=data.country,
        currency=data.currency or "INR",
        salary=0.0,
        is_active=True,
        is_verified=False,
        onboarding_complete=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "currency": user.currency,
                "onboarding_complete": user.onboarding_complete
            }
        }
    }


@router.post("/login", response_model=dict)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return JWT tokens."""
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "currency": user.currency,
                "onboarding_complete": user.onboarding_complete
            }
        }
    }


@router.post("/refresh", response_model=dict)
@limiter.limit("10/minute")
def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": str(user.id)})
    return {
        "success": True,
        "data": {"access_token": new_access, "token_type": "bearer"}
    }


@router.post("/forgot-password", response_model=dict)
@limiter.limit("3/minute")
def forgot_password(request: Request, data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Generate password reset token and send email."""
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if not user:
        # Don't reveal if email exists
        return {"success": True, "message": "If the email exists, a reset link has been sent"}

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # Send email (logs to console in dev)
    send_password_reset_email(user.email, token)

    return {
        "success": True,
        "message": "If the email exists, a reset link has been sent"
    }


@router.post("/reset-password", response_model=dict)
@limiter.limit("5/minute")
def reset_password(request: Request, data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using token."""
    user = db.query(User).filter(
        User.reset_token == data.token,
        User.reset_token_expiry > datetime.utcnow(),
        User.is_active == True
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.password_hash = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"success": True, "message": "Password reset successfully"}


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "salary": float(current_user.salary) if current_user.salary else 0,
            "currency": current_user.currency,
            "country": current_user.country,
            "occupation": current_user.occupation,
            "risk_profile": current_user.risk_profile,
            "onboarding_complete": current_user.onboarding_complete,
            "is_verified": current_user.is_verified
        }
    }


@router.put("/me", response_model=dict)
def update_me(data: OnboardingData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile."""
    if data.country is not None:
        current_user.country = data.country
    if data.occupation is not None:
        current_user.occupation = data.occupation
    if data.salary is not None:
        current_user.salary = data.salary
    if data.currency is not None:
        current_user.currency = data.currency
    if data.risk_profile is not None:
        current_user.risk_profile = data.risk_profile

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "salary": float(current_user.salary) if current_user.salary else 0,
            "currency": current_user.currency,
            "country": current_user.country,
            "occupation": current_user.occupation,
            "risk_profile": current_user.risk_profile
        }
    }


@router.post("/onboarding", response_model=dict)
def complete_onboarding(data: OnboardingData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Complete onboarding flow."""
    if data.country is not None:
        current_user.country = data.country
    if data.occupation is not None:
        current_user.occupation = data.occupation
    if data.salary is not None:
        current_user.salary = data.salary
    if data.currency is not None:
        current_user.currency = data.currency
    if data.risk_profile is not None:
        current_user.risk_profile = data.risk_profile

    current_user.onboarding_complete = True
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Onboarding completed successfully",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "onboarding_complete": True
        }
    }


@router.post("/logout", response_model=dict)
def logout():
    """Client-side logout - token is invalidated on client."""
    return {"success": True, "message": "Logged out successfully"}

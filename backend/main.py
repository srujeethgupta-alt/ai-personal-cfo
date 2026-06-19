import logging
import os
from rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

from auth import get_password_hash, verify_password
from database import engine, Base, db_session
from models import User
from migrate import migrate as run_migrations
from routers import dashboard, users, expenses, investments, loans, goals, budgets, ai, ai_tools, auth, notifications

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

# Sentry error tracking (production only)
SENTRY_DSN = os.getenv("SENTRY_DSN")
if IS_PROD and SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
    )
    logger.info("Sentry initialized for production")

# Hide API docs in production
docs_url = None if IS_PROD else "/docs"
redoc_url = None if IS_PROD else "/redoc"

app = FastAPI(
    title="AI Money Manager API",
    description="Production-grade AI-powered financial platform API",
    version="2.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url
)

# CORS origins - middleware added last so it wraps all responses (including errors)
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]


def _cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin")
    if origin and origin in allow_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


def _error_response(request: Request, status_code: int, content: dict) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=_cors_headers(request),
    )


class ForceCORSMiddleware(BaseHTTPMiddleware):
    """Ensure CORS headers are present on every response, including 500 errors."""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error("Middleware caught exception: %s", exc, exc_info=True)
            response = _error_response(
                request, 500, {"success": False, "error": "Internal server error", "detail": str(exc)}
            )
        origin = request.headers.get("origin")
        if origin and origin in allow_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Vary"] = "Origin"
        return response


# Rate limiting (inner middleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS outermost — added last so every response includes CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(ForceCORSMiddleware)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return _error_response(
        request, exc.status_code, {"success": False, "error": exc.detail}
    )

def _sanitize_validation_errors(errors):
    sanitized = []
    for err in errors:
        item = dict(err)
        if isinstance(item.get("input"), bytes):
            item["input"] = item["input"].decode("utf-8", errors="replace")
        sanitized.append(item)
    return sanitized


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detail = _sanitize_validation_errors(exc.errors())
    logger.warning(f"Validation error: {detail}")
    return _error_response(
        request, 422, {"success": False, "error": "Validation error", "detail": detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return _error_response(
        request, 500, {"success": False, "error": "Internal server error", "detail": str(exc)}
    )

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(expenses.router)
app.include_router(investments.router)
app.include_router(loans.router)
app.include_router(goals.router)
app.include_router(budgets.router)
app.include_router(ai_tools.router)
app.include_router(ai.router)
app.include_router(notifications.router)

@app.get("/")
def home():
    response = {
        "success": True,
        "message": "AI Money Manager API v2.0.0 Running Successfully",
    }
    if not IS_PROD:
        response["docs"] = "/docs"
    return response

@app.get("/health")
def health_check():
    return {"success": True, "status": "healthy"}


def seed_default_admin():
    """Create default admin user if it doesn't exist. Called once on startup."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123")
    try:
        with db_session() as db:
            existing = db.query(User).filter(User.email == admin_email).first()
            if existing:
                if not verify_password(admin_password, existing.password_hash):
                    existing.password_hash = get_password_hash(admin_password)
                    db.commit()
                    logger.info("Reset admin password hash for %s", admin_email)
                else:
                    logger.info("Default admin already exists: %s", admin_email)
                return

            admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                name="Administrator",
                country="India",
                currency="INR",
                salary=0.0,
                is_active=True,
                is_verified=True,
                onboarding_complete=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            logger.info("Created default admin user: %s", admin_email)
    except Exception as e:
        logger.error("Failed to seed default admin: %s", e, exc_info=True)


# Run migrations and seed admin ONCE when the app starts via a lifespan event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up AI Money Manager API...")
    run_migrations()
    Base.metadata.create_all(bind=engine)
    seed_default_admin()
    yield
    logger.info("Shutting down AI Money Manager API...")

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

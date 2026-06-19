import os
import threading
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_money_manager.db")
IS_POSTGRES = DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")

# SQLite is not thread-safe; serialize DB access in dev to prevent concurrent crashes.
_db_lock = threading.Lock() if not IS_POSTGRES else None

if IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 30},
        poolclass=NullPool,
        echo=False
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Enable foreign key constraints for SQLite only
if not IS_POSTGRES:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


@contextmanager
def db_session():
    """Thread-safe session for scripts/startup code outside FastAPI dependencies."""
    if _db_lock:
        _db_lock.acquire()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        if _db_lock:
            _db_lock.release()


def get_db():
    """
    Dependency that yields a database session and ensures cleanup.
    Use as FastAPI dependency: db: Session = Depends(get_db)
    """
    if _db_lock:
        _db_lock.acquire()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        if _db_lock:
            _db_lock.release()

"""Database connection setup.

Reads the connection string from the DATABASE_URL environment
variable (see .env.example). No credentials are hardcoded here.

Kept intentionally simple: a single SQLAlchemy engine + sessionmaker,
tables created with Base.metadata.create_all() (no migration
framework), matching the rest of this project's "reuse what's
simplest" approach.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Engine/session are created lazily-but-eagerly at import time when
# DATABASE_URL is configured, so a misconfigured deployment fails
# fast and loudly instead of failing deep inside a request handler.
# When DATABASE_URL is not set (e.g. running the existing Streamlit
# app / CLI, or importing this module in a context that doesn't need
# the DB), engine/SessionLocal stay None and get_db() raises a clear
# error only if something actually tries to use the database.
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if engine is not None
    else None
)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""

    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in your environment "
            "or .env file (see .env.example) to use the chat/history API."
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they don't already exist.

    Simple, migration-free setup as requested for Phase 1. Safe to
    call on every API startup - it's a no-op for tables that already
    exist.
    """

    if engine is None:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in your environment "
            "or .env file (see .env.example) to use the chat/history API."
        )

    from database import models  # noqa: F401  (registers models on Base)

    Base.metadata.create_all(bind=engine)

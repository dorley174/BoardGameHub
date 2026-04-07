"""Minimal database setup for the standalone users slice."""
from __future__ import annotations
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./boardgamehub.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

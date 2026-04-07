"""SQLAlchemy models for BoardGameHub."""
from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(length=50, collation="NOCASE"),
        unique=True,
        index=True,
        nullable=False,
    )

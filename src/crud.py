"""CRUD helpers."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate


def create_user(db: Session, user_in: UserCreate) -> User:
    """Persist a new user in the database."""
    user = User(username=user_in.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    """Return a user by primary key."""
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    """Return a user by username.

    The users.username column uses SQLite's NOCASE collation, so exact
    equality is already case-insensitive.
    """
    normalized_username = username.strip()
    statement = select(User).where(User.username == normalized_username)
    return db.scalar(statement)

"""CRUD helpers for the users slice."""
from __future__ import annotations
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate


def create_user(session: Session, user_in: UserCreate) -> User:
    """Persist a new user in the database."""
    existing_user = get_user_by_username(session, user_in.userName)
    if existing_user is not None:
        raise ValueError("Username already exists.")
    
    user = User(userName=user_in.userName)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> User | None:
    """Return a user by primary key."""
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    """Return a user by username."""
    return (
        session.query(User)
        .filter(func.lower(User.userName) == username.lower())
        .first()
    )

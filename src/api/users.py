"""API routes for user management."""
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from .. import crud, schemas
from ..db import get_session

router = APIRouter(prefix="/users", tags=["users"])
DbSession = Annotated[Session, Depends(get_session)]


@router.post(
    "",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    user_in: schemas.UserCreate,
    db: DbSession,
) -> schemas.UserRead:
    """Create a new user with a unique username."""
    try:
        return crud.create_user(db, user_in)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        ) from exc


@router.get(
    "/search",
    response_model=schemas.UserRead,
    summary="Find a user by username",
)
def get_user_by_username(
    username: Annotated[str, Query(min_length=1, max_length=50)],
    db: DbSession,
) -> schemas.UserRead:
    """Find a user by username."""
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    summary="Get a user by id",
)
def get_user(user_id: int, db: DbSession) -> schemas.UserRead:
    """Return a user by numeric identifier."""
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user
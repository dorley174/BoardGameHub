"""API routes for game collection management."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from .. import crud, schemas
from ..db import get_session

router = APIRouter(prefix="/users/{user_id}/games", tags=["games"])
DbSession = Annotated[Session, Depends(get_session)]


@router.post(
    "",
    response_model=schemas.UserGameRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a game to a user's collection",
)
def add_game_to_user(
    user_id: int,
    game_in: schemas.UserGameCreate,
    db: DbSession,
) -> schemas.UserGameRead:
    """Add a board game to a specific user's collection."""
    try:
        return crud.add_game_to_user(db, user_id, game_in)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Game already exists in user's collection.",
        ) from exc


@router.get(
    "",
    response_model=list[schemas.UserGameRead],
    summary="List all games owned by a user",
)
def list_user_games(
    user_id: int,
    db: DbSession,
) -> list[schemas.UserGameRead]:
    """Return the games that belong to a user."""
    try:
        return crud.list_user_games(db, user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{user_game_id}/status",
    response_model=schemas.UserGameRead,
    summary="Change a user's game availability status",
)
def update_user_game_status(
    user_id: int,
    user_game_id: int,
    status_in: schemas.UserGameStatusUpdate,
    db: DbSession,
) -> schemas.UserGameRead:
    """Toggle the availability flag of a user's game."""
    try:
        return crud.update_user_game_availability(
            db,
            user_id,
            user_game_id,
            status_in.isAvailable,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{user_game_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a game from a user's collection",
)
def remove_user_game(
    user_id: int,
    user_game_id: int,
    db: DbSession,
) -> Response:
    """Delete a game from a user's collection."""
    try:
        crud.remove_game_from_user(db, user_id, user_game_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)

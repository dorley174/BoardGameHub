"""API routes for group management."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..db import get_session
from .. import schemas
from ..services import group_service

router = APIRouter(prefix="/groups", tags=["groups"])
DbSession = Annotated[Session, Depends(get_session)]


@router.post(
    "",
    response_model=schemas.GroupRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new group",
)
def create_group(
    group_in: schemas.GroupCreate,
    db: DbSession,
):
    return group_service.create_group(db, group_in)


@router.post(
    "/{group_id}/members",
    response_model=schemas.GroupMemberRead,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to a group by username",
)
def invite_member(
    group_id: int,
    invite_in: schemas.GroupInvite,
    db: DbSession,
):
    return group_service.invite_member(db, group_id, invite_in)


@router.get(
    "/{group_id}/members",
    response_model=list[schemas.GroupMemberRead],
    summary="List group members",
)
def list_members(
    group_id: int,
    db: DbSession,
):
    return group_service.list_members(db, group_id)


@router.get(
    "/{group_id}/games",
    response_model=list[schemas.GroupGameRead],
    summary="List collective games of the group",
)
def list_games(
    group_id: int,
    db: DbSession,
):
    return group_service.list_games(db, group_id)

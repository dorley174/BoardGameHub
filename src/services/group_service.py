from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session

from .. import crud, schemas


def create_group(session: Session, group_in: schemas.GroupCreate):
    creator = crud.get_user(session, group_in.creatorUserId)
    if creator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator user not found.",
        )

    group = crud.create_group(session, group_in)
    crud.add_group_member(session, group.groupId, creator.userId)
    return group


def invite_member(
    session: Session,
    group_id: int,
    invite_in: schemas.GroupInvite,
) -> schemas.GroupMemberRead:
    group = crud.get_group(session, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    inviter = crud.get_user(session, invite_in.invitedByUserId)
    if inviter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inviting user not found.",
        )

    if group.creatorUserId != inviter.userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the group creator can invite members.",
        )

    invited_user = crud.get_user_by_username(session, invite_in.username)
    if invited_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to invite not found.",
        )

    existing_membership = crud.get_group_member(
        session,
        group_id=group_id,
        user_id=invited_user.userId,
    )
    if existing_membership is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this group.",
        )

    crud.add_group_member(session, group_id, invited_user.userId)

    return schemas.GroupMemberRead(
        groupId=group_id,
        userId=invited_user.userId,
        userName=invited_user.userName,
    )


def list_members(
    session: Session,
    group_id: int,
) -> list[schemas.GroupMemberRead]:
    group = crud.get_group(session, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    users = crud.list_group_members(session, group_id)
    return [
        schemas.GroupMemberRead(
            groupId=group_id,
            userId=user.userId,
            userName=user.userName,
        )
        for user in users
    ]


def list_games(
    session: Session,
    group_id: int,
) -> list[schemas.GroupGameRead]:
    group = crud.get_group(session, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    rows = crud.list_group_games(session, group_id)
    return [schemas.GroupGameRead(**row._mapping) for row in rows]
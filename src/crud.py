"""CRUD helpers for the users and groups slices."""
from __future__ import annotations

from sqlmodel import Session, select

from .models import Game, Group, GroupMember, User, UserGame
from .schemas import GroupCreate, UserCreate


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
    statement = select(User).where(User.userName == username)
    return session.exec(statement).first()


def create_group(session: Session, group_in: GroupCreate) -> Group:
    """Create a new group."""
    group = Group(
        groupName=group_in.groupName,
        creatorUserId=group_in.creatorUserId,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_group(session: Session, group_id: int) -> Group | None:
    """Return a group by primary key."""
    return session.get(Group, group_id)


def add_group_member(session: Session, group_id: int, user_id: int) -> GroupMember:
    """Add a user to a group."""
    membership = GroupMember(userId=user_id, groupId=group_id)
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def get_group_member(
    session: Session,
    group_id: int,
    user_id: int,
) -> GroupMember | None:
    """Return a membership record if it exists."""
    statement = select(GroupMember).where(
        GroupMember.groupId == group_id,
        GroupMember.userId == user_id,
    )
    return session.exec(statement).first()


def list_group_members(session: Session, group_id: int) -> list[User]:
    """Return all users in a group."""
    statement = (
        select(User)
        .join(GroupMember, GroupMember.userId == User.userId)
        .where(GroupMember.groupId == group_id)
        .order_by(User.userName)
    )
    return list(session.exec(statement).all())


def list_group_games(session: Session, group_id: int):
    """Return all game rows owned by group members."""
    statement = (
        select(
            Group.groupId.label("groupId"),
            Group.groupName.label("groupName"),
            User.userId.label("userId"),
            User.userName.label("userName"),
            Game.gameId.label("gameId"),
            Game.gameName.label("gameName"),
            UserGame.isAvailable.label("isAvailable"),
        )
        .select_from(Group)
        .join(GroupMember, GroupMember.groupId == Group.groupId)
        .join(User, User.userId == GroupMember.userId)
        .join(UserGame, UserGame.userId == User.userId)
        .join(Game, Game.gameId == UserGame.gameId)
        .where(Group.groupId == group_id)
        .order_by(User.userName, Game.gameName)
    )
    return session.exec(statement).all()

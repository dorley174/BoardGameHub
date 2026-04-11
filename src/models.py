from __future__ import annotations

from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    userId: Optional[int] = Field(default=None, primary_key=True)
    userName: str = Field(index=True, unique=True)


class Game(SQLModel, table=True):
    __tablename__ = "games"

    gameId: Optional[int] = Field(default=None, primary_key=True)
    gameName: str = Field(index=True)


class UserGame(SQLModel, table=True):
    __tablename__ = "user_games"
    __table_args__ = (
        UniqueConstraint("userId", "gameId", name="uq_user_game"),
    )

    userGameId: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="users.userId")
    gameId: int = Field(foreign_key="games.gameId")
    isAvailable: bool = Field(default=True)


class Group(SQLModel, table=True):
    __tablename__ = "groups"

    groupId: Optional[int] = Field(default=None, primary_key=True)
    groupName: str = Field(index=True)
    creatorUserId: int = Field(foreign_key="users.userId")


class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("userId", "groupId", name="uq_group_member"),
    )

    groupMemberId: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="users.userId")
    groupId: int = Field(foreign_key="groups.groupId")
from sqlmodel import Field, SQLModel
from typing import Optional


class User(SQLModel, table=True):
    userId: Optional[int] = Field(default=None, primary_key=True)
    userName: str = Field(index=True)


class Game(SQLModel, table=True):
    gameId: Optional[int] = Field(default=None, primary_key=True)
    gameName: str = Field(index=True)


class UserGame(SQLModel, table=True):
    userGameId: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="user.userId")
    gameId: int = Field(foreign_key="game.gameId")
    isAvailable: bool = Field(default=True)


class Group(SQLModel, table=True):
    groupId: Optional[int] = Field(default=None, primary_key=True)
    groupName: str = Field(index=True)
    creatorUserId: int = Field(foreign_key="user.userId")


class GroupMember(SQLModel, table=True):
    groupMemerId: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="user.userId")
    groupId: int = Field(foreign_key="group.groupId")

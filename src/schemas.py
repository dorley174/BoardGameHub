"""Schemas for BoardGameHub."""
from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{2,49}$")


class UserBase(BaseModel):
    """Common user fields."""

    userName: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["alice_01"],
        description="Unique username used across the application.",
    )

    @field_validator("userName")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Trim and validate username format."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Username must not be empty.")
        if not _USERNAME_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Username may contain letters, numbers, underscores, "
                "dots, or hyphens."
            )
        return normalized


class UserCreate(UserBase):
    """Schema used to create a user."""


class UserRead(UserBase):
    """Schema returned from API responses."""

    userId: int
    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    """Common game fields."""

    gameName: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Catan"],
        description="Display name of the board game.",
    )

    @field_validator("gameName")
    @classmethod
    def validate_game_name(cls, value: str) -> str:
        """Trim and validate a game title."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Game name must not be empty.")
        return normalized


class UserGameCreate(GameBase):
    """Schema used to add a game to a user's collection."""

    isAvailable: bool = Field(
        default=True,
        description="Whether the game is currently available.",
    )


class UserGameStatusUpdate(BaseModel):
    """Schema used to change a game's availability."""

    isAvailable: bool = Field(
        ...,
        description="New availability status for the game.",
    )


class UserGameRead(BaseModel):
    """Schema returned for a game owned by a user."""

    userGameId: int
    userId: int
    gameId: int
    gameName: str
    isAvailable: bool


class GroupBase(BaseModel):
    groupName: str = Field(..., min_length=1, max_length=100)


class GroupCreate(GroupBase):
    creatorUserId: int = Field(gt=0)


class GroupRead(GroupBase):
    groupId: int
    creatorUserId: int
    model_config = ConfigDict(from_attributes=True)


class GroupInvite(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    invitedByUserId: int = Field(gt=0)


class GroupMemberRead(BaseModel):
    groupId: int
    userId: int
    userName: str
    model_config = ConfigDict(from_attributes=True)


class GroupGameRead(BaseModel):
    groupId: int
    groupName: str
    userId: int
    userName: str
    gameId: int
    gameName: str
    isAvailable: bool
    model_config = ConfigDict(from_attributes=True)

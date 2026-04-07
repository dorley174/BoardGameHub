"""Schemas for BoardGameHub."""
from __future__ import annotations
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{2,49}$")


class UserBase(BaseModel):
    """Common user fields."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["alice_01"],
        description="Unique username used across the application.",
    )

    @field_validator("username")
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
    id: int
    model_config = ConfigDict(from_attributes=True)

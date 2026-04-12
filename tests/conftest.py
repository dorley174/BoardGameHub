"""Shared pytest fixtures for the BoardGameHub test suite."""
from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_session  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture()
def test_engine() -> Iterator[Engine]:
    """Create an in-memory SQLite engine for tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def session(test_engine: Engine) -> Iterator[Session]:
    """Provide a SQLModel session for direct DB setup in tests."""
    with Session(test_engine) as db_session:
        yield db_session


@pytest.fixture()
def client(test_engine: Engine) -> Iterator[TestClient]:
    """Provide a test client using the same in-memory database."""

    def override_get_session() -> Iterator[Session]:
        with Session(test_engine) as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_session, None)

from __future__ import annotations

from typing import Any

from sqlmodel import SQLModel, Session, create_engine

from . import models  # noqa: F401


class Database:
    """Simple database wrapper used by the application."""

    def __init__(self, db_path: str = "BoardGameHub.db") -> None:
        self.db_path = db_path
        self.engine: Any | None = None

    def connect(self):
        """Create the SQLite engine and initialize tables once."""
        if self.engine is None:
            self.engine = create_engine(
                f"sqlite:///{self.db_path}",
                echo=False,
                connect_args={"check_same_thread": False},
            )
            SQLModel.metadata.create_all(self.engine)
        return self.engine

    def get_engine(self):
        """Return an initialized engine."""
        return self.connect()


db = Database()


def get_session():
    """Yield a database session for FastAPI dependencies."""
    with Session(db.get_engine()) as session:
        yield session

from __future__ import annotations
from fastapi import FastAPI
from .api.users import router as users_router
from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BoardGameHub",
    description="Board game library tracker API.",
    version="0.1.0",
)
app.include_router(users_router)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint."""
    return {"status": "ok"}

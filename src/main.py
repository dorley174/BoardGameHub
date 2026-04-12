import os

import dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.games import router as games_router
from .api.groups import router as groups_router
from .api.users import router as users_router
from .db import db


dotenv.load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = FastAPI(title="BoardGameHub")


@app.on_event("startup")
def on_startup():
    db.connect()


@app.get("/")
def app_root(request: Request):
    return {"message": "BoardGameHub API"}


@app.get("/health")
def health(request: Request):
    return {"status": "ok"}


app.include_router(users_router)
app.include_router(games_router)
app.include_router(groups_router)


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    if exception.status_code == 404 and exception.detail == "Not Found":
        return JSONResponse(
            {
                "error": "Not Found",
                "message": "Endpoint does not exist",
            },
            status_code=404,
        )

    return JSONResponse(
        {"detail": exception.detail},
        status_code=exception.status_code,
    )


@app.exception_handler(Exception)
def internal_server_error(request: Request, exception: Exception):
    return JSONResponse(
        {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
        status_code=500,
    )


if __name__ == "__main__":
    import uvicorn

    db.connect()
    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=DEBUG)

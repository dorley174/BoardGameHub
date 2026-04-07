from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import dotenv
import os

from sqlmodel import Session
from .db import Database
from .api.users import router as users_router

# Configuration
dotenv.load_dotenv()
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Application and database
app = FastAPI()
db = Database()


def get_session():
    with Session(db.get_engine()) as session:
        yield session


@app.get("/")
def app_root(request: Request):
    return {}


@app.get("/health")
def app_root(request: Request):
    return {'status': 'ok'}


app.include_router(users_router)


@app.exception_handler(404)
def not_found(request: Request, exception: Exception):
    return JSONResponse(
        {
            "error": "Not Found",
            "message": "Endpoint does not exist"
        },
        status_code=404
    )


@app.exception_handler(500)
def internal_server_error(request: Request, exception: Exception):
    return JSONResponse(
        {
            "error": "Internal Server Error",
            "message": "An unexpected error ocured"
        },
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    db.connect()
    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=DEBUG)

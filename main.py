from fastapi import FastAPI, Request, status
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from ipaddress import ip_address
from src.conf.config import settings
from src.routes import auth, contacts, users, db, seed
from pathlib import Path

from typing import Callable

import re
import redis.asyncio as redis
import uvicorn


app = FastAPI()

banned_ips = [
    # ip_address("127.0.0.1"),
    ip_address("0.0.0.1"),
]

user_agent_ban_list = [r"Googlebot", r"Somebot", r"Python-urllib"]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
# directory = BASE_DIR.joinpath("src").joinpath("static")
# directory = BASE_DIR.joinpath("static")
# app.mount("/static", StaticFiles(directory=directory), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
async def root(request: Request):
    """
    The greeting message.
    """
    # return {"message": "Welcome! This is Homework 14"}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "Welcome! This is Homework 14",
            "about_app": "Contacts App main page",
        },
    )


app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(db.router, prefix="/api")
app.include_router(seed.router, prefix="")


# @app.on_event("startup")
async def startup_app():
    """
    A function that runs when the program starts.
    """
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


app.add_event_handler("startup", startup_app)


# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     """
#     ips ban function
#     """
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         print(f"{ip = }")
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
#         )
#     response = await call_next(request)
#     return response


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    user agent ban function
    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            print(f"{ban_pattern = }")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)

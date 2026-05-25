# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.database import engine
from api.routers import customers, orders
from frontend.routers import auth, pages

# uvicorn main:app --reload


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-to-a-long-random-string",
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(orders.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(pages.router)
app.include_router(auth.router)

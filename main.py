# main.py
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.config import settings
from api.database import engine
from api.routers import customers, orders
from api.security import backend_auth
from frontend.routers import auth, pages

# uvicorn main:app --reload
# docker compose up -d


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    max_age=1800,
    https_only=True,
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

api_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(backend_auth.require_auth)],
)

api_router.include_router(customers.router)
api_router.include_router(orders.router)

app.include_router(api_router)
app.include_router(pages.router)
app.include_router(auth.router)

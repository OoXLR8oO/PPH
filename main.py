# main.py
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from api.config import settings
from api.database import engine
from api.limiter import limiter
from api.routers import customers, orders
from api.security import backend_auth
from frontend.routers import auth, pages

# uvicorn main:app --reload
# docker compose up -d


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def rate_limit_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, RateLimitExceeded)
    return _rate_limit_exceeded_handler(request, exc)


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_handler,
)

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

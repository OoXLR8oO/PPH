# main.py
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.database import engine
from api.limiter import limiter
from api.routers import customers, orders
from api.security.jwt_auth import get_current_user
from api.security.middleware import SecurityHeadersMiddleware
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
    SecurityHeadersMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

api_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(customers.router)
api_router.include_router(orders.router)

app.include_router(api_router)
app.include_router(pages.router)
app.include_router(auth.router)

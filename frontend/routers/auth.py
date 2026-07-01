import asyncio

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.limiter import limiter
from api.security.backend_auth import DUMMY_PASSWORD_HASH, verify_password
from api.security.jwt_auth import create_access_token
from api.services.user import get_user_by_username

FAILURE_DELAY = 0.3

router = APIRouter(tags=["Auth"])


@router.post("/api/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(get_db),
):
    username = username.strip().lower()

    user = await get_user_by_username(db, username)
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    is_valid = verify_password(password, password_hash)

    await asyncio.sleep(FAILURE_DELAY)

    if not user or not is_valid:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid username or password"},
        )

    token = create_access_token(user.id)

    return JSONResponse(
        content={"access_token": token, "token_type": "bearer"},
    )


@router.post("/api/logout")
async def logout():
    return JSONResponse(content={"detail": "ok"})

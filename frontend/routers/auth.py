# frontend/routers/auth.py
import asyncio

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.limiter import limiter
from api.models import User
from api.security.backend_auth import DUMMY_PASSWORD_HASH, verify_password
from api.security.jwt_auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_user_from_refresh_token,
)
from api.services.auth import get_user_by_username, rotate_refresh_token

FAILURE_DELAY = 0.3

router = APIRouter(tags=["Auth"])


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
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

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, user.refresh_token_version)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 15,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24,
        path="/refresh",
    )

    return {
        "detail": "ok",
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/refresh")

    return {
        "detail": "ok",
    }


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_from_refresh_token(
        request.cookies.get("refresh_token"),
        db,
    )

    await rotate_refresh_token(db, user)

    new_refresh_token = create_refresh_token(
        user.id,
        user.refresh_token_version,
    )

    new_access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 15,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
        path="/refresh",
    )

    return {"detail": "ok"}


@router.get("/me")
@limiter.limit("20/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
    }

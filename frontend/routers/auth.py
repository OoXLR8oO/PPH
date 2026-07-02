import asyncio

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.limiter import limiter
from api.models import User
from api.security.backend_auth import DUMMY_PASSWORD_HASH, verify_password
from api.security.jwt_auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from api.services.auth import get_user_by_username

FAILURE_DELAY = 0.3

router = APIRouter(tags=["Auth"])


@router.post("/api/login")
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
    refresh_token = create_refresh_token(user.id)

    # request.session["access_token"] = access_token

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
        path="/refresh",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {
        "detail": "ok",
    }


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    user_id = verify_refresh_token(refresh_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    result = await db.execute(select(User).where(User.id == user_id_int))

    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(user.id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }

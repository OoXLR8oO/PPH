# frontend/routers/auth.py
import asyncio

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.limiter import limiter
from api.security.password import DUMMY_PASSWORD_HASH, verify_password
from api.services.user import get_user_by_username
from frontend.templates_config import templates

FAILURE_DELAY = 0.3

router = APIRouter(tags=["Auth"])


@router.post("/login")
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
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "error": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user_id"] = user.id

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

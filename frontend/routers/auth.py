from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from api.config import settings
from frontend.templates_config import templates

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    if username != settings.admin_username or password != settings.admin_password:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid username or password",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["authenticated"] = True

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

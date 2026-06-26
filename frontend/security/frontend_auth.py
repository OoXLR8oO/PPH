# frontend/security/frontend_auth.py
from fastapi import HTTPException, Request, status


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)


def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )

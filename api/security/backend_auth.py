# api/security/backend_auth.py
from fastapi import HTTPException, Request, status


def require_auth(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

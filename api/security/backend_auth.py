# api/security/backend_auth.py
from fastapi import HTTPException, Request, status

print("BACKEND AUTH MODULE LOADED")


def require_auth(request: Request):
    print("BACKEND AUTH HIT")
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

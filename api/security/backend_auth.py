# api/security/backend_auth.py
from fastapi import HTTPException, Request, status
from pwdlib import PasswordHash


def require_auth(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


_password_hash = PasswordHash.recommended()

DUMMY_PASSWORD_HASH = _password_hash.hash("dummy-password")


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)

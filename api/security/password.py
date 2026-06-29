# api/security/password.py
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()

DUMMY_PASSWORD_HASH = _password_hash.hash("dummy-password")


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)

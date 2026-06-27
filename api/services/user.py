# api/services/user.py
from sqlalchemy import func, select

from api.models import User


async def get_user_by_username(db, username: str):
    username = username.strip().lower()

    result = await db.execute(select(User).where(func.lower(User.username) == username))
    return result.scalar_one_or_none()

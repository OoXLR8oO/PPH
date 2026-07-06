# api/services/auth.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import User


async def get_user_by_username(db, username: str):
    username = username.strip().lower()

    result = await db.execute(select(User).where(func.lower(User.username) == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))

    return result.scalar_one_or_none()


async def rotate_refresh_token(db: AsyncSession, user: User) -> None:
    user.refresh_token_version += 1
    await db.commit()
    await db.refresh(user)

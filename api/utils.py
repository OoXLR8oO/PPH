# api/utils.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Order


async def get_next_order_code(db: AsyncSession) -> str:
    result = await db.execute(
        select(Order.order_code)
    )

    used = {
        int(code)
        for code in result.scalars()
        if code.isdigit()
    }

    for i in range(10000):
        if i not in used:
            return f"{i:04d}"

    raise ValueError("All 4-digit order codes are in use")
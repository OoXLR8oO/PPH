# api/utils.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Order


async def get_next_order_code(db: AsyncSession) -> str:
    result = await db.execute(select(Order.order_code))

    used = {int(code) for code in result.scalars() if code.isdigit()}

    for i in range(10000):
        if i not in used:
            return f"{i:04d}"

    raise ValueError("All 4-digit order codes are in use")


def generate_batch_code(order_codes: list[str]) -> str:
    if not order_codes:
        raise ValueError("Cannot generate batch code without orders")

    if len(order_codes) == 1:
        return order_codes[0]

    return f"{order_codes[0]}-{order_codes[-1]}"


async def get_next_order_codes(
    db: AsyncSession,
    quantity: int,
) -> list[str]:
    result = await db.execute(select(Order.order_code))

    used = {int(code) for code in result.scalars() if code.isdigit()}

    consecutive = 0
    start = 0

    for i in range(10000):
        if i in used:
            consecutive = 0
            start = i + 1
            continue

        consecutive += 1

        if consecutive == quantity:
            return [f"{code:04d}" for code in range(start, i + 1)]

    raise ValueError("Not enough available order codes")

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

    codes = []

    for i in range(10000):
        if i not in used:
            codes.append(f"{i:04d}")

            if len(codes) == quantity:
                return codes

    raise ValueError("Not enough available order codes")

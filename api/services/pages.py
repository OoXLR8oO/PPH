from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api import models


async def get_index_data(view: str, search: str | None, db: AsyncSession):
    search = search.strip() if search else None

    context = {
        "view": view,
        "search": search,
    }

    if view == "customers":
        stmt = select(models.Customer)

        if search:
            stmt = stmt.where(
                (models.Customer.name.ilike(f"%{search}%"))
                | (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Customer.id.desc())
        result = await db.execute(stmt)

        context["customers"] = result.scalars().all()

    else:
        stmt = select(models.Order).options(joinedload(models.Order.customer))

        if search:
            stmt = stmt.join(models.Customer).where(
                (models.Order.order_code.ilike(f"%{search}%"))
                | (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Order.id.desc())
        result = await db.execute(stmt)

        context["orders"] = result.scalars().all()

    return context


async def get_order_edit_page(order_code: str, db: AsyncSession):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    result = await db.execute(stmt)
    order = result.scalars().first()

    return order


async def get_customer_edit_page(customer_id: int, db: AsyncSession):
    stmt = select(models.Customer).where(models.Customer.id == customer_id)

    result = await db.execute(stmt)
    customer = result.scalars().first()

    return customer

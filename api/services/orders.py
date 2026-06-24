# api/services/orders.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api import models, schemas
from api.enums import OrderStatus
from api.utils import get_next_order_code


async def list_orders(
    status: OrderStatus | None,
    needs_print: bool | None,
    name: str | None,
    email: str | None,
    exact_email: bool,
    skip: int,
    limit: int,
    db: AsyncSession,
):
    stmt = (
        select(models.Order)
        .join(models.Customer)
        .options(joinedload(models.Order.customer))
    )

    if status is not None:
        stmt = stmt.where(models.Order.status == status)

    if needs_print is not None:
        stmt = stmt.where(models.Order.needs_print == needs_print)

    if name:
        stmt = stmt.where(models.Customer.name.ilike(f"%{name}%"))

    if email:
        if exact_email:
            stmt = stmt.where(models.Customer.email == email.lower())
        else:
            stmt = stmt.where(models.Customer.email.ilike(f"%{email}%"))

    stmt = stmt.order_by(models.Order.id.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_order_by_code(order_code: str, db: AsyncSession):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def create_order(order: schemas.OrderCreate, db: AsyncSession):
    email = order.customer.email.strip().lower()

    # 1. Find or create customer
    stmt = select(models.Customer).where(models.Customer.email == email)
    result = await db.execute(stmt)
    customer = result.scalars().first()

    if not customer:
        customer = models.Customer(
            name=order.customer.name,
            email=email,
            phone=order.customer.phone,
            notes=order.customer.notes,
        )
        db.add(customer)
        await db.flush()  # ensure customer.id exists

    # 2. Create order with retry logic
    for _ in range(5):
        code = await get_next_order_code(db)

        new_order = models.Order(
            order_code=code,
            customer_id=customer.id,
            film_type=order.film_type,
            needs_print=order.needs_print,
            notes=order.notes,
        )

        db.add(new_order)

        try:
            await db.commit()

            result = await db.execute(
                select(models.Order)
                .options(joinedload(models.Order.customer))
                .where(models.Order.id == new_order.id)
            )

            return result.scalars().first()

        except IntegrityError:
            await db.rollback()

    return None


async def update_order(
    order_code: str,
    payload: schemas.OrderUpdate,
    db: AsyncSession,
):
    order = await get_order_by_code(order_code, db)

    if not order:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)

    return order


async def delete_order(order_code: str, db: AsyncSession):
    order = await get_order_by_code(order_code, db)

    if not order:
        return None

    await db.delete(order)
    await db.commit()

    return order

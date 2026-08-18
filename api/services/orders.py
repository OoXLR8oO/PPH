# api/services/orders.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api import models, schemas
from api.enums import OrderStatus
from api.services import batches
from api.utils import generate_batch_code, get_next_order_codes


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


async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession,
):
    email = order.customer.email.strip().lower()

    try:
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
            await db.flush()

        # 2. Generate order codes
        order_codes = await get_next_order_codes(
            db,
            order.quantity,
        )

        # 3. Create batch
        batch = models.Batch(
            batch_code=generate_batch_code(order_codes),
            dropbox_link=None,
            customer_id=customer.id,
        )

        db.add(batch)
        await db.flush()

        # 4. Create orders
        for code in order_codes:
            new_order = models.Order(
                order_code=code,
                customer_id=customer.id,
                batch_id=batch.id,
                film_type=order.film_type,
                needs_print=order.needs_print,
                notes=order.notes,
            )

            db.add(new_order)

        await db.commit()

        # 5. Reload with relationships
        result = await db.execute(
            select(models.Batch)
            .options(joinedload(models.Batch.orders).joinedload(models.Order.customer))
            .where(models.Batch.id == batch.id)
        )

        return result.unique().scalar_one()

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


async def delete_order(
    order_code: str,
    db: AsyncSession,
):
    order = await get_order_by_code(order_code, db)

    if not order:
        return None

    batch_id = order.batch_id

    await db.delete(order)
    await db.flush()

    if batch_id:
        result = await db.execute(
            select(models.Order.id).where(models.Order.batch_id == batch_id).limit(1)
        )

        if result.scalar_one_or_none() is None:
            await batches.delete_batch(
                batch_id,
                db,
                commit=False,
            )

    await db.commit()

    return order

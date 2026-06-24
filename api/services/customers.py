# api/services/customers_service.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api import models, schemas


class DuplicateCustomerError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


async def list_customers(email: str | None, skip: int, limit: int, db: AsyncSession):
    stmt = select(models.Customer)

    if email:
        stmt = stmt.where(models.Customer.email == email.lower())

    stmt = stmt.offset(skip).limit(min(limit, 100))

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_customer_by_id(customer_id: int, db: AsyncSession):
    stmt = select(models.Customer).where(models.Customer.id == customer_id)

    result = await db.execute(stmt)
    return result.scalars().first()


async def create_customer(customer: schemas.CustomerCreate, db: AsyncSession):
    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        notes=customer.notes,
    )

    db.add(new_customer)

    try:
        await db.commit()
        await db.refresh(new_customer)
        return new_customer

    except IntegrityError:
        await db.rollback()
        raise DuplicateCustomerError()


async def update_customer(
    customer_id: int,
    payload: schemas.CustomerUpdate,
    db: AsyncSession,
):
    customer = await get_customer_by_id(customer_id, db)

    if not customer:
        return None

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(customer, k, v)

    await db.commit()
    await db.refresh(customer)
    return customer


async def delete_customer(customer_id: int, db: AsyncSession):
    customer = await get_customer_by_id(customer_id, db)

    if not customer:
        return None

    await db.delete(customer)
    await db.commit()
    return customer

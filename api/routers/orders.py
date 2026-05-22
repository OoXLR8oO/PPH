from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api import models, schemas
from api.database import get_db
from api.utils import get_next_order_code
from api.enums import OrderStatus


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[schemas.OrderResponse])
async def list_orders(
    status: OrderStatus | None = None,
    needs_print: bool | None = None,
    name: str | None = None,
    email: str | None = None,
    exact_email: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    limit = min(limit, 100)

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


@router.get("/{order_code}", response_model=schemas.OrderResponse)
async def get_order(
    order_code: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.post("/", response_model=schemas.OrderResponse)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    email = order.customer.email.strip().lower()

    customer_stmt = select(models.Customer).where(
        models.Customer.email == email
    )

    result = await db.execute(customer_stmt)
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

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate unique order code",
    )


@router.patch("/{order_code}", response_model=schemas.OrderResponse)
async def update_order(
    order_code: str,
    payload: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)

    return order


@router.delete("/{order_code}")
async def delete_order(
    order_code: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.Order).where(
        models.Order.order_code == order_code
    )

    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    await db.delete(order)
    await db.commit()

    return {"message": "Order deleted"}
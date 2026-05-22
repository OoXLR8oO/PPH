# api/routers/customers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api import models, schemas
from api.database import get_db


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[schemas.CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 50,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    limit = min(limit, 100)

    stmt = select(models.Customer)

    if email:
        stmt = stmt.where(models.Customer.email == email.lower())

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    customers = result.scalars().all()

    return customers


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
async def get_customer_by_id(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.Customer).where(
        models.Customer.id == customer_id
    )

    result = await db.execute(stmt)
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.post("/", response_model=schemas.CustomerResponse)
async def create_customer(
    customer: schemas.CustomerCreate,
    db: AsyncSession = Depends(get_db),
):
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

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email already exists",
        )


@router.patch("/{customer_id}", response_model=schemas.CustomerResponse)
async def update_customer(
    customer_id: int,
    payload: schemas.CustomerUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.Customer).where(
        models.Customer.id == customer_id
    )

    result = await db.execute(stmt)
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.Customer).where(
        models.Customer.id == customer_id
    )

    result = await db.execute(stmt)
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    await db.delete(customer)
    await db.commit()

    return {"message": "Customer deleted"}
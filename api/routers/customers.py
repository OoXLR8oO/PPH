# api/routers/customers.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import schemas
from api.database import get_db
from api.limiter import limiter
from api.services import customers

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get("", response_model=list[schemas.CustomerResponse])
@limiter.limit("60/minute")
async def list_customers(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await customers.list_customers(email, skip, limit, db)


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
@limiter.limit("40/minute")
async def get_customer_by_id(
    request: Request,
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    customer = await customers.get_customer_by_id(customer_id, db)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.post("", response_model=schemas.CustomerResponse)
@limiter.limit("10/minute")
async def create_customer(
    request: Request,
    customer: schemas.CustomerCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await customers.create_customer(customer, db)

    except customers.DuplicateCustomerError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email already exists",
        )


@router.patch("/{customer_id}", response_model=schemas.CustomerResponse)
@limiter.limit("10/minute")
async def update_customer(
    request: Request,
    customer_id: int,
    payload: schemas.CustomerUpdate,
    db: AsyncSession = Depends(get_db),
):
    customer = await customers.update_customer(customer_id, payload, db)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.delete("/{customer_id}")
@limiter.limit("5/minute")
async def delete_customer(
    request: Request,
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await customers.delete_customer(customer_id, db)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return {"message": "Customer deleted"}

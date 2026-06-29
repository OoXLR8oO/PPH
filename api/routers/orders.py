# api/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import schemas
from api.database import get_db
from api.enums import OrderStatus
from api.limiter import limiter
from api.services import orders

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("", response_model=list[schemas.OrderResponse])
@limiter.limit("60/minute")
async def list_orders(
    request: Request,
    status: OrderStatus | None = None,
    needs_print: bool | None = None,
    name: str | None = None,
    email: str | None = None,
    exact_email: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    return await orders.list_orders(
        status, needs_print, name, email, exact_email, skip, limit, db
    )


@router.get("/{order_code}", response_model=schemas.OrderResponse)
@limiter.limit("120/minute")
async def get_order(
    request: Request,
    order_code: str,
    db: AsyncSession = Depends(get_db),
):
    order = await orders.get_order_by_code(order_code, db)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.post("", response_model=schemas.OrderResponse)
@limiter.limit("60/minute")
async def create_order(
    request: Request,
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await orders.create_order(order, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        )

    return result


@router.patch("/{order_code}", response_model=schemas.OrderResponse)
@limiter.limit("60/minute")
async def update_order(
    request: Request,
    order_code: str,
    payload: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    order = await orders.update_order(order_code, payload, db)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.delete("/{order_code}")
@limiter.limit("10/minute")
async def delete_order(
    request: Request,
    order_code: str,
    db: AsyncSession = Depends(get_db),
):
    order = await orders.delete_order(order_code, db)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order deleted"}

# api/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from api import models, schemas
from api.database import get_db
from api.utils import get_next_order_code
from api.enums import OrderStatus


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[schemas.OrderResponse])
def list_orders(
    status: OrderStatus | None = None,
    needs_print: bool | None = None,
    name: str | None = None,
    email: str | None = None,
    exact_email: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    limit = min(limit, 100)

    query = (
        db.query(models.Order)
        .join(models.Customer)
        .options(joinedload(models.Order.customer))
    )

    if status is not None:
        query = query.filter(models.Order.status == status)

    if needs_print is not None:
        query = query.filter(models.Order.needs_print == needs_print)

    if name is not None:
        query = query.filter(models.Customer.name.ilike(f"%{name}%"))

    if email:
        if exact_email:
            query = query.filter(models.Customer.email == email)
        else:
            query = query.filter(models.Customer.email.ilike(f"%{email}%"))

    return (
        query.order_by(models.Order.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{order_code}", response_model=schemas.OrderResponse)
def get_order(order_code: str, db: Session = Depends(get_db)):
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.customer))
        .filter(models.Order.order_code == order_code)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )

    return order


@router.post("/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    customer = (
        db.query(models.Customer)
        .filter(models.Customer.email == order.customer.email)
        .first()
    )

    if not customer:
        customer = models.Customer(
            name=order.customer.name,
            email=order.customer.email,
            phone=order.customer.phone,
            notes=order.customer.notes
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # retry loop for safe order_code generation
    for _ in range(5):
        code = get_next_order_code(db)

        new_order = models.Order(
            order_code=code,
            customer_id=customer.id,
            film_type=order.film_type,
            needs_print=order.needs_print,
            notes=order.notes
        )

        db.add(new_order)

        try:
            db.commit()
            db.refresh(new_order)
            return new_order

        except IntegrityError:
            db.rollback()
            continue

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate unique order code"
    )


@router.patch("/{order_code}", response_model=schemas.OrderResponse)
def update_order(
    order_code: str,
    payload: schemas.OrderUpdate,
    db: Session = Depends(get_db),
):
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.customer))
        .filter(models.Order.order_code == order_code)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if payload.status is not None:
        order.status = payload.status

    if payload.film_type is not None:
        order.film_type = payload.film_type

    if payload.needs_print is not None:
        order.needs_print = payload.needs_print

    if payload.notes is not None:
        order.notes = payload.notes

    db.commit()
    db.refresh(order)

    return order


@router.delete("/{order_code}")
def delete_order(order_code: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.order_code == order_code
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )

    db.delete(order)
    db.commit()

    return {"message": "Order deleted"}
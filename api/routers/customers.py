# api/routers/customers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api import models, schemas
from api.database import get_db


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[schemas.CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),

    email: str | None = None,
):
    limit = min(limit, 10)

    query = db.query(models.Customer)

    if email is not None:
        query = query.filter(models.Customer.email == email.lower())

    customers = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return customers


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found"
        )

    return customer


@router.post("/", response_model=schemas.CustomerResponse)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    new_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        notes=customer.notes
    )

    db.add(new_customer)

    try:
        db.commit()
        db.refresh(new_customer)
        return new_customer

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email already exists"
        )


@router.patch("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int,
    payload: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if payload.name is not None:
        customer.name = payload.name

    if payload.email is not None:
        customer.email = payload.email

    if payload.phone is not None:
        customer.phone = payload.phone

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted"}
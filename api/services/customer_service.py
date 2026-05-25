# api/services/customer_service.py
from sqlalchemy.orm import Session

from api import models, schemas


def get_or_create_customer(
    db: Session, data: schemas.CustomerCreate
) -> models.Customer:
    customer = (
        db.query(models.Customer).filter(models.Customer.email == data.email).first()
    )

    if customer:
        return customer

    customer = models.Customer(name=data.name, email=data.email, phone=data.phone)

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer

# api/utils.py
import random
from sqlalchemy.orm import Session
from api.models import Order


def generate_unique_code(db: Session) -> str:
    while True:
        code = f"{random.randint(0, 9999):04d}"
        exists = db.query(Order).filter(Order.order_code == code).first()
        if not exists:
            return code


def get_next_order_code(db: Session) -> str:
    existing_codes = db.query(Order.order_code).all()

    used = set()

    for (code,) in existing_codes:
        if code.isdigit():
            used.add(int(code))

    for i in range(10000):
        if i not in used:
            return f"{i:04d}"

    raise ValueError("All 4-digit order codes are in use")


# def get_next_order_code(db: Session) -> str:
#     existing_codes = db.query(Order.order_code).all()

#     used = {int(code) for (code,) in existing_codes}

#     for i in range(10000):
#         if i not in used:
#             return f"{i:04d}"

#     raise ValueError("All 4-digit order codes are in use")
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
    # Fetch all existing codes
    existing_codes = db.query(Order.order_code).all()

    # Convert to a set of integers for fast lookup
    used = {int(code[0]) for code in existing_codes}

    # Find the first available code
    for i in range(10000):
        if i not in used:
            return f"{i:04d}"

    raise ValueError("All 4-digit order codes are in use")
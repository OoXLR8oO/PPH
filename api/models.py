# api/models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy import String, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from api.database import Base
from api.enums import FilmType, OrderStatus


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    orders: Mapped[list[Order]] = relationship("Order", back_populates="customer")

    @validates("email")
    def normalize_email(self, key, value):
        return value.lower()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_code: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        nullable=False
    )

    film_type: Mapped[FilmType] = mapped_column(
        Enum(FilmType, name="film_type"),
        nullable=False
    )

    needs_print: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )

    customer: Mapped[Customer] = relationship(
        back_populates="orders"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )
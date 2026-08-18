# api/models.py
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from api.database import Base
from api.enums import FilmType, OrderStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    refresh_token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    orders: Mapped[list[Order]] = relationship(
        "Order", back_populates="customer", cascade="all, delete-orphan"
    )

    batches: Mapped[list[Batch]] = relationship(
        "Batch",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    @validates("email")
    def normalize_email(self, key, value):
        return value.lower()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        nullable=False,
    )

    film_type: Mapped[FilmType] = mapped_column(
        Enum(FilmType, name="film_type"), nullable=False
    )

    needs_print: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="orders")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("batches.id", name="fk_orders_batch_id_batches", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    batch: Mapped[Batch] = relationship(back_populates="orders")


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_code: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    dropbox_link: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    customer: Mapped[Customer] = relationship(back_populates="batches")

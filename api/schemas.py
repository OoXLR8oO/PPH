# api/schemas.py
from datetime import datetime, timezone as dt_timezone
from pytz import timezone
from pydantic import BaseModel, EmailStr, field_serializer, field_validator, ConfigDict

from api.enums import FilmType, OrderStatus


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    notes: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr):
        return v.lower()


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    notes: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr | None):
        return v.lower() if v else v


class OrderCreate(BaseModel):
    customer: CustomerCreate
    film_type: FilmType
    needs_print: bool
    notes: str | None = None


class OrderResponse(BaseModel):
    id: int
    order_code: str
    status: OrderStatus
    film_type: FilmType
    needs_print: bool
    created_at: datetime
    customer: CustomerResponse
    notes: str | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt_timezone.utc)

        local_time = value.astimezone(timezone("Australia/Melbourne"))
        return local_time.strftime("%d-%m-%Y %H:%M:%S")

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    film_type: FilmType | None = None
    needs_print: bool | None = None
    notes: str | None = None
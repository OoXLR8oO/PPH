# frontend/routers/pages.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from api import models
from api.database import get_db


templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    view: str = "orders",
    search: str | None = None,
    db: Session = Depends(get_db),
):
    search = search.strip() if search else None

    context = {
        "request": request,
        "view": view,
        "search": search,
    }

    if view == "customers":
        stmt = select(models.Customer)

        if search:
            stmt = stmt.where(
                (models.Customer.name.ilike(f"%{search}%")) |
                (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Customer.id.desc())

        context["customers"] = db.execute(stmt).scalars().all()

    else:
        stmt = select(models.Order).options(
            joinedload(models.Order.customer)
        )

        if search:
            stmt = stmt.join(models.Customer).where(
                (models.Order.order_code.ilike(f"%{search}%")) |
                (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Order.id.desc())

        context["orders"] = db.execute(stmt).scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@router.get("/orders/{order_code}/edit", response_class=HTMLResponse)
def edit_order_page(
    request: Request,
    order_code: str,
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    order = db.execute(stmt).scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_order.html",
        context={
            "request": request,
            "order": order
        }
    )


@router.get("/orders/new", response_class=HTMLResponse)
def create_order_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_order.html",
        context={
            "request": request
        }
    )
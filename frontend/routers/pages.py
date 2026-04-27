# frontend/routers/pages.py
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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
    # Normalize once
    search = search.strip() if search else None

    context = {
        "request": request,
        "view": view,
        "search": search,
    }

    if view == "customers":
        query = db.query(models.Customer)

        if search:
            query = query.filter(
                (models.Customer.name.ilike(f"%{search}%")) |
                (models.Customer.email.ilike(f"%{search}%"))
            )

        context["customers"] = query.order_by(models.Customer.id.desc()).all()

    else:  # orders view
        query = db.query(models.Order).options(
            joinedload(models.Order.customer)
        )

        if search:
            query = query.join(models.Customer).filter(
                (models.Order.order_code.ilike(f"%{search}%")) |
                (models.Customer.email.ilike(f"%{search}%"))
            )

        context["orders"] = query.order_by(models.Order.id.desc()).all()

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

    return templates.TemplateResponse(
        request=request,
        name="edit_order.html",
        context={"order": order}
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
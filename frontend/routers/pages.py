from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from api import models
from api.database import get_db
from api.enums import OrderStatus, FilmType


templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Order)
        .options(joinedload(models.Order.customer))
    )

    if search:
        search = search.strip()

        query = query.join(models.Customer).filter(
            (models.Order.order_code.ilike(f"%{search}%")) |
            (models.Customer.email.ilike(f"%{search}%"))
        )

    orders = query.order_by(models.Order.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "orders": orders,
            "search": search
        },
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


@router.post("/orders/{order_code}/edit")
def update_order_template(
    order_code: str,
    order_status: str | None = Form(None),
    film_type: str | None = Form(None),
    needs_print: str | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.order_code == order_code
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order_status is not None:
        order.status = OrderStatus(order_status)

    if film_type is not None:
        order.film_type = FilmType(film_type)

    order.needs_print = needs_print == "true"

    if notes is not None:
        order.notes = notes.strip() or None

    db.commit()

    return RedirectResponse(
        url="/", 
        status_code=status.HTTP_303_SEE_OTHER
    )
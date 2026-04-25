# frontend/routers/pages.py
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from api import models
from api.database import get_db
from api.enums import OrderStatus, FilmType
from api.utils import get_next_order_code


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


@router.get("/orders/new", response_class=HTMLResponse)
def create_order_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_order.html",
        context={
            "request": request
        }
    )


@router.post("/orders/new")
def create_order_template(
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: str = Form(...),
    customer_notes: str | None = Form(None),
    film_type: str = Form(...),
    needs_print: str | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
):
    needs_print_bool = needs_print == "true"

    email = customer_email.strip().lower()

    customer = db.query(models.Customer).filter(
        models.Customer.email == email
    ).first()

    if not customer:
        customer = models.Customer(
            name=customer_name,
            email=email,
            phone=customer_phone,
            notes=customer_notes,
        )
        db.add(customer)
        db.flush()

    order_code = get_next_order_code(db)

    order = models.Order(
        order_code=order_code,
        customer_id=customer.id,
        film_type=film_type,
        needs_print=needs_print_bool,
        notes=notes,
        status=OrderStatus.PENDING,
    )

    db.add(order)
    db.commit()

    return RedirectResponse(
        url="/?view=orders", 
        status_code=status.HTTP_303_SEE_OTHER
    )
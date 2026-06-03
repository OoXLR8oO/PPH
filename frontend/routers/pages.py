# frontend/routers/pages.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api import models
from api.database import get_db
from frontend.templates_config import templates

router = APIRouter(tags=["Pages"])


def require_auth(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    auth=Depends(require_auth),
    view: str = "orders",
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    search = search.strip() if search else None

    context = {
        "request": request,
        "view": view,
        "search": search,
        "is_authenticated": is_authenticated(request),
    }

    if view == "customers":
        stmt = select(models.Customer)

        if search:
            stmt = stmt.where(
                (models.Customer.name.ilike(f"%{search}%"))
                | (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Customer.id.desc())

        result = await db.execute(stmt)
        context["customers"] = result.scalars().all()

    else:
        stmt = select(models.Order).options(joinedload(models.Order.customer))

        if search:
            stmt = stmt.join(models.Customer).where(
                (models.Order.order_code.ilike(f"%{search}%"))
                | (models.Customer.email.ilike(f"%{search}%"))
            )

        stmt = stmt.order_by(models.Order.id.desc())

        result = await db.execute(stmt)
        context["orders"] = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@router.get("/orders/{order_code}/edit", response_class=HTMLResponse)
async def edit_order_page(
    request: Request,
    order_code: str,
    auth=Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(models.Order)
        .options(joinedload(models.Order.customer))
        .where(models.Order.order_code == order_code)
    )

    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_order.html",
        context={
            "request": request,
            "order": order,
            "is_authenticated": is_authenticated(request),
        },
    )


@router.get("/orders/new", response_class=HTMLResponse)
async def create_order_page(
    request: Request,
    auth=Depends(require_auth),
):
    return templates.TemplateResponse(
        request=request,
        name="create_order.html",
        context={
            "request": request,
            "is_authenticated": is_authenticated(request),
        },
    )


@router.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer_page(
    request: Request,
    customer_id: int,
    auth=Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.Customer).where(models.Customer.id == customer_id)

    result = await db.execute(stmt)
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_customer.html",
        context={
            "request": request,
            "customer": customer,
            "is_authenticated": is_authenticated(request),
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "is_authenticated": is_authenticated(request),
        },
    )

# frontend/routers/pages.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.services import pages
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
    context = await pages.get_index_data(view, search, db)

    context.update(
        {
            "request": request,
            "is_authenticated": is_authenticated(request),
        }
    )

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
    db=Depends(get_db),
):
    order = await pages.get_order_edit_page(order_code, db)

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
    db=Depends(get_db),
):
    customer = await pages.get_customer_edit_page(customer_id, db)

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

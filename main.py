from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from api import models
from api.database import engine, get_db
from api.routers import orders, customers
from pathlib import Path


# uvicorn main:app --reload

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="frontend/templates")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(orders.router, prefix="/api")
app.include_router(customers.router, prefix="/api")


# @app.get("/")
# def index(request: Request):
#     return templates.TemplateResponse(
#         request=request,
#         name="index.html",
#         context={}
#     )


@app.get("/", response_class=HTMLResponse)
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

        query = query.filter(
            (models.Order.order_code.ilike(f"%{search}%")) |
            (models.Customer.email.ilike(f"%{search}%"))
        ).join(models.Customer)

    orders = query.order_by(models.Order.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "orders": orders,
            "search": search
        },
    )
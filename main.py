# main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api import models
from api.database import engine
from api.routers import orders, customers

from frontend.routers import pages


# uvicorn main:app --reload

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="frontend/templates")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(orders.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(pages.router)


# @app.get("/")
# def index(request: Request):
#     return templates.TemplateResponse(
#         request=request,
#         name="index.html",
#         context={}
#     )
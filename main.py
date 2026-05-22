# main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api import models
from api.database import engine

from api.routers import customers, orders
from frontend.routers import pages


# uvicorn main:app --reload

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

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
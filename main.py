# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.database import engine
from api.routers import customers, orders

from frontend.routers import pages


# uvicorn main:app --reload


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

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
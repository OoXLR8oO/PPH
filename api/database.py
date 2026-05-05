# api/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./orders.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def get_db():
    with SessionLocal() as db:
        yield db
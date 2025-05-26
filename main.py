from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Generator

SQLALCHEMY_DATABASE_URL = 'sqlite:///./items.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Item(Base):
    __table_name__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Float, nullable=True)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=True)

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int

    class Config:
        org_mode = True


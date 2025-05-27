from sqlalchemy import Column, Integer, String, Float
from database import Base

class Item(Base):
    __tablename__ = 'items'
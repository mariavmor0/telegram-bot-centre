from sqlalchemy import Column, Integer, String, Float
from database import Base

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Float, nullable=True)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=True)
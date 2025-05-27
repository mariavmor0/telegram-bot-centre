from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    name: Optional [str]
    description: Optional[str]
    price: Optional[float]
    tax: Optional[float]

class ItemOut(BaseModel):
    id: int

    class Config:
        org_mode = True
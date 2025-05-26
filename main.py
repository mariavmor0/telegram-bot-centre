from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.mypy.plugin import SQLAlchemyPlugin
from sqlalchemy.orm import sessionmaker, declarative_base, Session

SQLALCHEMY_DATABASE_URL = 'sqlite:///./items.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(bind=engine, autoflash=False, autocommit=False)

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    tax = Column(Float, nullable=True)

class ItemCreate(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemOut(ItemCreate):
    pass

app = FastAPI

@app.post('/items')
async def create_item(item: Item):
    for existing in items:
        if existing.id == item.id:
            return{'error': 'ID уже существует'}
    items.append(item)
    return {'message': 'Элемент создан', 'item': item}

@app.get('/items')
async def get_all_items():
    return items

@app.get('/items/{item_id}')
async def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    return{'error':'Элемент не найден'}

@app.put('/items/{item_id}')
def update_item(item_id: int, new_item: Item):
    for item in items:
        if item.id == item_id:
            item.name = new_item.name
            item.description = new_item.description
            item.price = new_item.price
            item.tax = new_item.tax
            return {'message': 'Элемент обновлен', 'item': item}
    return {'error': 'Элемент не найден'}

@app.delete('/items/{item_id}')
def delete_item(item_id: int):
    for item in items:
        if item.id == item_id:
            items.remove(item)
            return {'message': 'Элемент удален', 'item': item}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)


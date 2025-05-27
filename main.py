from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine
from models import Base, Item
from schemas import ItemCreate, ItemUpdate, ItemOut

app = FastAPI()

@app.on_event('startup')
def on_startup():
    Base.metadata.create_all(bing=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/items', response_model=ItemOut)
def create_item (item: ItemCreate, db: Session = Depends(get_db)):
    new_item = Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get('/items/{item_id}', response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item

@app.put('/items/{item_id}', response_model=ItemOut)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')

    for key, value in item_update.dict().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

@app.delete('/items/{item_id}')
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')

    db.delete(item)
    db.commit()
    return{'message': 'Item deleted'}

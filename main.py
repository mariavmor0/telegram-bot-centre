from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Item
from schemas import ItemCreate, ItemUpdate, ItemOut

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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


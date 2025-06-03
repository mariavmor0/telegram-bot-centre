from http.client import responses

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
created_item_id = None

def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'hello from FastAPI'}

def test_create_item():
    global created_item_id
    response = client.post('/items/', json={
       'name': 'Test Item',
        'description': 'A test item',
        'price': 100.0,
        'tax': 20.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Test Item'
    assert data['price'] == 100.0
    created_item_id = data['id']

def test_read_item():
    response = client.get(f'/items/{created_item_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == created_item_id
    assert data['name'] == 'Test Item'

def test_update_item():
    response = client.put(f'/items/{created_item_id}', json={
        'name': 'Updated Item',
        'price': 150.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Updated Item'
    assert data['price'] == 150.0

def test_delete_item():
    response = client.delete(f'/items/{created_item_id}')
    assert response.status_code == 200
    data = response.json()
    assert 'has been deleted' in data['message']
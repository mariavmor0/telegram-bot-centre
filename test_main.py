from http.client import responses

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_item():
    response = client.post('/items/', json={
        'name': 'Test item',
        'description': 'A simple test item',
        'price': 9.99,
        'tax': 1.00
    })
    assert response.status_code == 200
    assert response.json()['name'] == 'Test item'
    assert response.json()['price'] == 9.99

def test_read_items():
    response = client.get('/items/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_items():
    post_response = client.post('/items/', json={
        'name': 'GetTest',
        'description': 'for GET',
        'price': 5.5,
        'tax': 0.5
    })
    item_id = post_response.json()['id']

    get_response = client.get(f'/items/{item_id}')
    assert get_response.status_code == 200
    assert get_response.json()['id'] == item_id
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
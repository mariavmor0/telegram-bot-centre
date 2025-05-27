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

def test_read_all_items():
    response = client.get('/items/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_single_items():
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

def test_update_item():
    post_response = client.post('/items/', json={
        'name': 'Old Name',
        'description': 'Old Desc',
        'price': 10.0,
        'tax': 1.0
    })
    item_id = post_response.json()['id']

    update_response = client.put(f'/items/{item_id}', json={
        'name': 'New Name',
        'price': 15.0
    })

    assert update_response.status_code == 200
    assert update_response.json()['name'] == 'New Name'
    assert update_response.json()['price'] == 15.0

def test_delete_item():
    post_responce = client.post('/items/', json={
        'name': 'To Delete',
        'description': 'To be deleted',
        'price': 3.0,
        'tax': 0.2
    })
    item_id = post_responce.json()['id']

    delete_response = client.delete(f'/items/{item_id}')
    assert delete_response.status_code == 200
    assert 'has been deleted' in delete_response.json()['message']

    get_response = client.get(f'/items/{item_id}')
    assert get_response.status_code == 200
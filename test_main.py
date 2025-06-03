from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
created_item_id = None

def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'hello from FastAPI'}

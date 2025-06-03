from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
created_item_id = None
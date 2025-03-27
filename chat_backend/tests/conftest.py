import pytest
from fastapi.testclient import TestClient

from chat_backend.main import app
from chat_backend.settings import settings
from chat_backend.database import SessionLocal, Base


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
    
    
@pytest.fixture
def headers(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    response = client.post("/login_user", json=user_data)
    response_data = response.json()

    return {
        "Authorization": f"Bearer {response_data['token']}",
        "Content-Type": "application/json"
    }
    
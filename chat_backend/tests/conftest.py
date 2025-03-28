import shutil

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from chat_backend.main import app
from chat_backend.settings import settings


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    assert settings.mode == "TEST"
    

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
    

@pytest.fixture
def upload_files_headers(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    response = client.post("/login_user", json=user_data)
    response_data = response.json()

    return {
        "Authorization": f"Bearer {response_data['token']}",
    }
    

@pytest.fixture(scope="function", autouse=True)
def clean_local_storage():
    """Fixture to clean testing local storage between tests."""
    if settings.file_storage_path.exists():
        shutil.rmtree(settings.file_storage_path)
        
    yield 

    if settings.file_storage_path.exists():
        shutil.rmtree(settings.file_storage_path)

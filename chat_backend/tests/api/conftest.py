import shutil

import pytest
from fastapi.testclient import TestClient

from chat_backend.main import app
from chat_backend.database import get_db
from chat_backend.tests.common_fixtures import *


@pytest.fixture
def valid_pdf() -> bytes:
    with open("./chat_backend/tests/files/valid.pdf", "rb") as file:
        return file.read()
    

@pytest.fixture
def client(db_session):
    session, _ = db_session
    
    def override_get_db():
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()
    
    
@pytest.fixture
def headers(client):
    user_data = {
        "email": settings.default_admin_email.get_secret_value(),
        "password": settings.default_admin_password.get_secret_value()
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
        "email": settings.default_admin_email.get_secret_value(),
        "password": settings.default_admin_password.get_secret_value()
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
    
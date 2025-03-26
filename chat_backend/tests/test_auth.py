import pytest
from fastapi.testclient import TestClient

from chat_backend.main import app
from chat_backend.settings import settings
from chat_backend.database.crud import get_user_by_email
from chat_backend.security.utils import hash_password


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_register_user(client):
    user_data = {
        "email": "test_register_user@email.ru",
        "password": settings.default_admin_password
    }

    response = client.post("/register_user", json=user_data)
    assert response.status_code == 201
    assert "token" in response.json()


def test_register_user_existing_email(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    client.post("/register_user", json=user_data)

    response = client.post("/register_user", json=user_data)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Пользователь с таким email уже существует"}


def test_login_user_success(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    client.post("/register_user", json=user_data)

    response = client.post("/login_user", json=user_data)

    assert response.status_code == 200
    assert "token" in response.json()


def test_login_user_invalid_email(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    client.post("/register_user", json=user_data)

    invalid_user_data = {
        "email": "wronguser@example.com",
        "password": settings.default_admin_password
    }
    response = client.post("/login_user", json=invalid_user_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Неправильный email или пароль"}


def test_login_user_invalid_password(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }
    client.post("/register_user", json=user_data)

    invalid_user_data = {
        "email": settings.default_admin_email,
        "password": "wrongpassword"
    }
    response = client.post("/login_user", json=invalid_user_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Неправильный email или пароль"}


def test_password_hashing(client):
    user_data = {
        "email": settings.default_admin_email,
        "password": settings.default_admin_password
    }

    session = client.app.state.db_session
    db_user = get_user_by_email(session, user_data["email"])
    
    print(hash_password(user_data["password"]))

    assert db_user.password != user_data["password"]
    assert db_user.password == hash_password(user_data["password"])

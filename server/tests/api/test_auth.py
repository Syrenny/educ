import pytest

from server.config import secrets
from server.database import get_user_by_email


# === Test Register ===
@pytest.mark.asyncio
async def test_register_user(client):
    user_data = {
        "email": "test_register_user@email.ru",
        "password": secrets.default_admin_password.get_secret_value(),
    }

    response = await client.post("/register_user", json=user_data)
    assert response.status_code == 201
    assert "token" in response.json()


@pytest.mark.asyncio
async def test_register_user_existing_email(client):
    user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": secrets.default_admin_password.get_secret_value(),
    }
    await client.post("/register_user", json=user_data)

    response = await client.post("/register_user", json=user_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Пользователь с таким email уже существует"}


@pytest.mark.asyncio
async def test_register_user_invalid_email(client):
    user_data = {
        "email": "invalid_email",
        "password": secrets.default_admin_password.get_secret_value(),
    }

    response = await client.post("/register_user", json=user_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_missing_password(client):
    user_data = {"email": "test_register_user_missing_password@email.ru"}

    response = await client.post("/register_user", json=user_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_empty_request(client):
    response = await client.post("/register_user", json={})

    assert response.status_code == 422


# === Test Login ===


@pytest.mark.asyncio
async def test_login_user_success(client):
    user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": secrets.default_admin_password.get_secret_value(),
    }
    await client.post("/register_user", json=user_data)

    response = await client.post("/login_user", json=user_data)

    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.asyncio
async def test_login_user_invalid_email(client):
    user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": secrets.default_admin_password.get_secret_value(),
    }
    await client.post("/register_user", json=user_data)

    invalid_user_data = {
        "email": "wronguser@example.com",
        "password": secrets.default_admin_password.get_secret_value(),
    }
    response = await client.post("/login_user", json=invalid_user_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Неправильный email или пароль"}


@pytest.mark.asyncio
async def test_login_user_invalid_password(client):
    user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": secrets.default_admin_password.get_secret_value(),
    }
    await client.post("/register_user", json=user_data)

    invalid_user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": "wrongpassword",
    }
    response = await client.post("/login_user", json=invalid_user_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Неправильный email или пароль"}


@pytest.mark.asyncio
async def test_password_hashing(db_session):
    session, _ = db_session
    user_data = {
        "email": secrets.default_admin_email.get_secret_value(),
        "password": secrets.default_admin_password.get_secret_value(),
    }
    db_user = await get_user_by_email(session, user_data["email"])

    assert db_user.password != user_data["password"]


# === Test Access Token ===


@pytest.mark.asyncio
async def test_access_with_invalid_token(client):
    response = await client.post(
        "/v1/chat/completions", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401

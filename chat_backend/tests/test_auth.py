from chat_backend.settings import settings
from chat_backend.database import get_user_by_email, get_db


# === Test Register ===

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
    
    
def test_register_user_invalid_email(client):
    user_data = {
        "email": "invalid_email",
        "password": settings.default_admin_password
    }

    response = client.post("/register_user", json=user_data)

    assert response.status_code == 422
    
    
def test_register_user_missing_password(client):
    user_data = {
        "email": "test_register_user_missing_password@email.ru"
    }

    response = client.post("/register_user", json=user_data)

    assert response.status_code == 422
    
    
def test_register_user_empty_request(client):
    response = client.post("/register_user", json={})

    assert response.status_code == 422


# === Test Login ===


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
    session = next(get_db())
    db_user = get_user_by_email(session, user_data["email"])
    
    assert db_user.password != user_data["password"]
    
    
# === Test Access Token ===

def test_access_with_invalid_token(client):
    response = client.post("/v1/chat/completions",
                          headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401

import hashlib
import hmac
from datetime import datetime, timedelta
from uuid import UUID

import bcrypt
import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

from server.config import config, secrets
from server.database.models import DBUser

bearer_auth = HTTPBearer()


def verify_access_token(token: str) -> dict:
    decoded_token = jwt.decode(
        token,
        secrets.jwt_secret_key.get_secret_value(),
        algorithms=[config.jwt_algorithm],
    )
    return decoded_token


def get_user_id(request: Request) -> UUID | None:
    """
    Extract and validate JWT token from access_token cookie.
    Returns user_id (UUID) if token is valid, else raises HTTPException(401).
    """
    token: str | None = None

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")

    try:
        payload = verify_access_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise ValueError("Missing user ID in token")
        return UUID(user_id)
    except (jwt.PyJWTError, ValueError) as err:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from err


def generate_access_token(db_user: DBUser) -> str:
    """
    Создает JWT токен с переданными данными и временем жизни.
    """
    to_encode = {"id": str(db_user.id)}
    expire = datetime.now() + timedelta(minutes=config.jwt_token_expires_minutes)
    to_encode.update({"exp": str(expire)})

    encoded_jwt = jwt.encode(
        to_encode,
        secrets.jwt_secret_key.get_secret_value(),
        algorithm=config.jwt_algorithm,
    )

    return encoded_jwt


def generate_signature(file_id: str, expires: int) -> str:
    """Генерация подписи для ссылки"""
    data = f"{file_id}:{expires}".encode()
    return hmac.new(
        secrets.sign_secret_key.get_secret_value().encode(), data, hashlib.sha256
    ).hexdigest()


# === Passwords ===


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))

from uuid import UUID
from datetime import datetime, timedelta

import jwt
import hmac
import bcrypt
import hashlib
from loguru import logger
from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from chat_backend.database.models import DBUser
from chat_backend.settings import settings


bearer_auth = HTTPBearer()


def verify_access_token(token: str) -> dict:
    decoded_token = jwt.decode(
        token, 
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm]
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
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def generate_access_token(db_user: DBUser) -> str:
    """
    Создает JWT токен с переданными данными и временем жизни.
    """
    to_encode = {
        "id": str(db_user.id)
    }
    expire = datetime.now() + timedelta(minutes=settings.jwt_token_expires_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key.get_secret_value(
    ), algorithm=settings.jwt_algorithm)
    
    return encoded_jwt


def generate_signature(file_id: str, expires: int) -> str:
    """Генерация подписи для ссылки"""
    data = f'{file_id}:{expires}'.encode()
    return hmac.new(settings.sign_secret_key.encode(), data, hashlib.sha256).hexdigest()
    
    
# === Passwords ===

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

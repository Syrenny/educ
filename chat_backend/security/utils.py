from datetime import datetime, timedelta

import jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from chat_backend.database.models import DBUser
from chat_backend.settings import settings


bearer_auth = HTTPBearer()


def verify_access_token(token: str):
    """
    Проверяет токен и возвращает его декодированные данные.
    """
    try:
        decoded_token = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return decoded_token
    except jwt.PyJWTError:
        return None


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_auth)) -> int | None:
    """
    Check and retrieve authentication information from custom bearer token.

    :param credentials Credentials provided by Authorization header
    :type credentials: HTTPAuthorizationCredentials
    :return: Decoded user_id or None if token is invalid
    :rtype: TokenModel | None
    """
    token = credentials.credentials
    decoded = verify_access_token(token)
    
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return decoded["id"]


def generate_access_token(db_user: DBUser) -> str:
    """
    Создает JWT токен с переданными данными и временем жизни.
    """
    to_encode = {
        "id": db_user.id
    }
    expire = datetime.now() + timedelta(minutes=settings.jwt_token_expires_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    return encoded_jwt
    
    
# === Passwords ===

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение пароля с хешем."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

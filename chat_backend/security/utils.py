from datetime import datetime, timedelta

import jwt
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from chat_backend.models import TokenModel
from chat_backend.settings import settings


bearer_auth = HTTPBearer()


def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_auth)) -> TokenModel:
    """
    Check and retrieve authentication information from custom bearer token.

    :param credentials Credentials provided by Authorization header
    :type credentials: HTTPAuthorizationCredentials
    :return: Decoded token information or None if token is invalid
    :rtype: TokenModel | None
    """

    ...


def generate_access_token(data: dict) -> str:
    """
    Создает JWT токен с переданными данными и временем жизни.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.jwt_token_expires_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Проверяет токен и возвращает его декодированные данные.
    """
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return decoded_token
    except jwt.PyJWTError:
        return None
    
    
# === Passwords ===
def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение пароля с хешем."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

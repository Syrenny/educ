from pydantic import BaseModel, EmailStr, field_validator

from .utils import (
    generate_access_token,
    generate_signature,
    get_user_id,
    hash_password,
    verify_access_token,
    verify_password,
)


class UserModel(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password", mode="before")
    @classmethod
    def validate_empty(cls, value: str):
        if value == "":
            raise ValueError("Поле пароля не должно быть пустым")
        return value


__all__ = [
    "generate_access_token",
    "generate_signature",
    "get_user_id",
    "hash_password",
    "verify_access_token",
    "verify_password",
    "UserModel",
]

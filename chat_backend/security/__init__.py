from pydantic import BaseModel, field_validator, EmailStr

from .utils import *


class UserModel(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("password", mode="before")
    def validate_empty(cls, value: str):
        if value == "":
            raise ValueError("Поле пароля не должно быть пустым")
        return value


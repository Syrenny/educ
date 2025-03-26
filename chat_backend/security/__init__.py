from pydantic import BaseModel, field_validator, EmailStr
from fastapi import APIRouter, Request, HTTPException

from chat_backend.security.utils import *
from chat_backend.database.crud import (
    create_user,
    get_user_by_email,
    create_token
)
from .utils import (
    generate_access_token,
    verify_access_token,
    hash_password,
    verify_password
)


router = APIRouter()


class UserModel(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password', mode='after')
    def validate_password(cls, v):
        cls.hashed_password = hash_password(v)
        return v 


@router.post("/resister_user", tags=["Security"])
async def register_user(user: UserModel):
    session = router.state.db_session
    if get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    else:
        db_user = create_user(
            session, 
            user.email, 
            user.password
        )
        token = generate_access_token(dict(db_user))
        db_token = create_token(
            session,
            db_user.id,
            token
        )
        
        
@router.post("/login_user")
async def login_user(user: UserModel):
    session = router.state.db_session
    if db_user := get_user_by_email(session, user.email):
        if not verify_access_token(user.token.token):
            token = generate_access_token(dict(db_user))
            create_token(
                session,
                db_user.id,
                token
            )
    else:
        raise HTTPException(
            status_code=401, detail="Неправильный email или пароль")

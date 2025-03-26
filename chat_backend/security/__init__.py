from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, field_validator, EmailStr

from chat_backend.database.crud import (
    create_user,
    get_user_by_email,
    create_token
)
from .utils import (
    generate_access_token,
    hash_password,
    verify_password,
    get_user_id
)


router = APIRouter()


class UserModel(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password', mode='before')
    def validate_password(cls, v: str) -> str:
        return hash_password(v)


@router.post("/register_user", tags=["Security"], status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserModel,
    request: Request
    ):
    session = request.app.state.db_session
    if get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    db_user = create_user(
        session, 
        user.email, 
        user.password
    )
    token = generate_access_token(db_user)
    create_token(
        session,
        db_user.id,
        token
    )
    
    return {
        "token": token
    }
        
        
@router.post("/login_user")
async def login_user(
    user: UserModel,
    request: Request
    ):
    session = request.app.state.db_session
    db_user = get_user_by_email(session, user.email)
    
    if not db_user or not verify_password(db_user.password, user.password):
        raise HTTPException(
            status_code=401, detail="Неправильный email или пароль"
        )

    token = generate_access_token(db_user)
    create_token(
        session,
        db_user.id,
        token
    )
            
    return {
        "token": token
    }

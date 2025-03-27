from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, status, Depends

from chat_backend.database import (
    create_user,
    get_user_by_email,
    create_token,
    get_db
)
from chat_backend.security import (
    generate_access_token,
    verify_password,
    UserModel,
    hash_password
)


router = APIRouter()


@router.post("/register_user", tags=["Security"], status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserModel,
    session: Session = Depends(get_db)
):
    if get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    db_user = create_user(
        session,
        user.email,
        hash_password(user.password)
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
    session: Session = Depends(get_db)
):
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

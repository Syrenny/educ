from uuid import UUID 

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, status, Depends

from chat_backend.database import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_token,
    get_db,
)
from chat_backend.security import (
    generate_access_token,
    verify_password,
    UserModel,
    hash_password,
    get_user_id
)


router = APIRouter()


@router.post("/register_user", tags=["Security"], status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserModel,
    session: AsyncSession = Depends(get_db)
):
    if await get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    db_user = await create_user(
        session,
        user.email,
        hash_password(user.password)
    )
    token = generate_access_token(db_user)
    await create_token(
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
    session: AsyncSession = Depends(get_db)
):
    db_user = await get_user_by_email(session, user.email)
    if not db_user or not verify_password(db_user.password, user.password):
        raise HTTPException(
            status_code=401, detail="Неправильный email или пароль"
        )

    token = generate_access_token(db_user)
    await create_token(
        session,
        db_user.id,
        token
    )

    return {
        "token": token
    }
    
    
@router.get("/me")
async def me(
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> str:
    db_user = await get_user_by_id(
        session=session,
        user_id=user_id
    )
    return db_user.email
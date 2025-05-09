from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import (
    create_token,
    create_user,
    get_db,
    get_user_by_email,
    get_user_by_id,
)
from server.security import (
    UserModel,
    generate_access_token,
    get_user_id,
    hash_password,
    verify_password,
)

router = APIRouter()


@router.post("/register_user", tags=["Security"], status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserModel, session: AsyncSession = Depends(get_db)
) -> JSONResponse:
    if await get_user_by_email(session, user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        ) from None
    db_user = await create_user(session, user.email, hash_password(user.password))

    await session.flush()

    if db_user is None:
        raise HTTPException(
            status_code=500, detail="Error while creating user"
        ) from None

    token = generate_access_token(db_user)

    await create_token(session, db_user.id, token)

    await session.commit()
    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"email": db_user.email},
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=timedelta(days=7),
        path="/",
    )

    return response


@router.post("/login_user")
async def login_user(
    user: UserModel,
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    db_user = await get_user_by_email(session, user.email)
    if not db_user or not verify_password(db_user.password, user.password):
        raise HTTPException(status_code=401, detail="Неправильный email или пароль")

    token = generate_access_token(db_user)
    await create_token(session, db_user.id, token)
    response = JSONResponse(
        status_code=200,
        content={"email": db_user.email},
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=timedelta(days=7),
        path="/",
    )

    return response


@router.get("/me")
async def me(
    user_id: UUID = Depends(get_user_id), session: AsyncSession = Depends(get_db)
) -> JSONResponse:
    db_user = await get_user_by_id(session=session, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(
        status_code=200,
        content={"email": db_user.email},
    )


@router.post("/logout", tags=["Security"], status_code=200)
async def logout(response: Response) -> JSONResponse:
    response.delete_cookie(key="access_token", path="/")

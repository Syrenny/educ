from uuid import UUID
import logging

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import *
from chat_backend.models import FileMeta, ShortcutModel


logger = logging.getLogger(__name__)
        
        
async def list_file_meta(
    session: AsyncSession,
    user_id: UUID
) -> list[DBFileMeta]:
    stmt = select(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
    )

    result = await session.execute(stmt)

    return result.scalars().all()
        
        
async def add_file_meta(
    session: AsyncSession,
    user_id: UUID,
    filename: str
    ) -> DBFileMeta:
    file_meta = DBFileMeta(
        user_id=user_id,
        filename=filename,
    )
    session.add(file_meta)
    
    await session.flush()
    
    return file_meta


async def find_file_meta(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID
) -> None | DBFileMeta:
    stmt = select(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id
    )

    result = await session.execute(stmt)

    return result.scalars().first()


async def find_user(
    session: AsyncSession,
    file_id: UUID
) -> None | DBUser:
    stmt = select(DBFileMeta).options(
        joinedload(DBFileMeta.user)
    ).filter(DBFileMeta.file_id == file_id)

    result = await session.execute(stmt)

    return result.scalars().first().user


async def delete_file_meta(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
    ) -> None | DBFileMeta:    
    db_file_meta = await find_file_meta(session, user_id, file_id)

    if db_file_meta:
        await session.delete(db_file_meta)

    return db_file_meta


async def create_user(
    session: AsyncSession, 
    email: str, 
    password: str
    ) -> DBUser | None:
    """Создает нового пользователя."""
    try:
        user = DBUser(email=email, password=password)
        session.add(user)
        return user
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Ошибка при создании пользователя (IntegrityError): {e}")
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise


async def get_user_by_email(
    session: AsyncSession, 
    email: str
    ) -> DBUser | None:
    """Возвращает пользователя по email, или None, если пользователь не найден."""
    result = await session.execute(select(DBUser).filter(DBUser.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession,
    user_id: UUID
    ) -> DBUser | None:
    result = await session.execute(
        db.select(DBUser).filter(DBUser.id == user_id)
    )
    return result.scalars().first()


async def create_token(
    session: AsyncSession, 
    user_id: UUID,
    token: str
    ) -> DBToken:
    """Создает токен для пользователя."""
    try:
        result = await session.execute(select(DBToken).filter(DBToken.user_id == user_id))
        existing_token = result.scalar_one_or_none()

        if existing_token:
            existing_token.token = token
        else:
            existing_token = DBToken(user_id=user_id, token=token)
            session.add(existing_token)

        return existing_token
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при создании токена: {e}")
        raise


async def save_file_chunks(
    session: AsyncSession,
    user_id: UUID,
    meta: FileMeta,
    chunks: list[str]
) -> None:
    """Сохраняет чанки в БД."""
    try:
        chunk_objects = [
            DBChunk(
                user_id=user_id,
                filename=meta.filename,
                file_id=meta.file_id,
                chunk_text=chunk
            )
            for chunk in chunks
        ]
        session.add_all(chunk_objects)
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при сохранении чанков: {e}")
        raise


async def find_file_chunks(
    session: AsyncSession,
    query: str,
    user_id: UUID,
    file_id: UUID
) -> list[str]:
    """Ищет чанки с помощью pg_trgm."""
    try:
        result = await session.execute(
            db.select(DBChunk).filter(
                DBChunk.user_id == user_id,
                DBChunk.file_id == file_id,
                DBChunk.chunk_text.op('~')(query)
            )
        )
        db_chunks = result.scalars().all()
        
        return [db_chunk.chunk_text for db_chunk in db_chunks]
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске чанков: {e}")
        return []


async def delete_file_chunks(
    session: AsyncSession,
    user_id: UUID,
    filename: str,
    file_id: UUID
) -> None:
    """Удаляет чанки, связанные с файлом пользователя."""
    try:
        await session.execute(
            db.delete(DBChunk).filter_by(
                user_id=user_id,
                filename=filename,
                file_id=file_id
            )
        )
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при удалении чанков: {e}")
        raise
    
    
async def set_indexed(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
    ) -> bool:
    stmt = select(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id,
    )
    
    result = await session.execute(stmt)
    db_file_meta = result.scalars().first()
    if db_file_meta:
        db_file_meta.is_indexed = True
        return True
    return False


async def is_indexed(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
) -> bool | None:
    db_file_meta = await find_file_meta(
        session=session,
        user_id=user_id,
        file_id=file_id
    )
    if db_file_meta is None:
        return None
    return db_file_meta.is_indexed


async def add_message(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
    content: str,
    is_user: bool,
    shortcut: ShortcutModel | None = None,
) -> DBMessage:
    new_message = DBMessage(
        user_id=user_id,
        file_id=file_id,
        content=content,
        is_user_message=is_user,
        action=shortcut.action.value if shortcut else None,
        snippet=shortcut.content if shortcut else None
    )

    session.add(new_message)
    await session.flush()

    return new_message
    
    
async def get_messages(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID
) -> list[DBMessage] | None:
    result = await session.execute(
        db.select(DBMessage).filter(
            DBMessage.user_id == user_id,
            DBMessage.file_id == file_id
        ).order_by(DBMessage.timestamp)
    )
    return result.scalars().all()

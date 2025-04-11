from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import *
from chat_backend.models import FileMeta


logger = logging.getLogger(__name__)
        
        
async def list_file_meta(
    session: AsyncSession,
    user_id: UUID
) -> list[DBFileMeta]:
    result = await session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
    )
    return result.all()
        
        
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
    result = await session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id
    )
    return result.first()


async def delete_file_meta(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
    ) -> None | DBFileMeta:    
    if file_meta := await find_file_meta(session, user_id, file_id):
        await session.delete(file_meta)

    return file_meta


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
    result = await session.query(DBUser).filter(DBUser.email == email)
    return result.first()


async def get_user_by_id(
    session: AsyncSession,
    user_id: UUID
    ) -> DBUser | None:
    result = await session.query(DBUser).filter(DBUser.id == user_id)
    return result.first()


async def create_token(
    session: AsyncSession, 
    user_id: UUID,
    token: str
    ) -> DBToken:
    """Создает токен для пользователя."""
    try:
        existing_token = await session.query(
            DBToken).filter_by(user_id=user_id).first()

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
        session.bulk_save_objects(chunk_objects)
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при сохранении чанков: {e}")
        raise


async def find_file_chunks(
    session: AsyncSession,
    query: str,
    user_id: UUID,
    file_id: UUID
) -> list[DBChunk]:
    """Ищет чанки с помощью pg_trgm."""
    try:
        return await session.query(DBChunk).filter(
            DBChunk.user_id == user_id,
            DBChunk.file_id == file_id,
            DBChunk.chunk_text.op('~')(query)
        ).all()
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
        await session.query(DBChunk).filter_by(
            user_id=user_id,
            filename=filename,
            file_id=file_id
        ).delete(synchronize_session=False)
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при удалении чанков: {e}")
        raise
    
    
async def set_indexed(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID,
    ) -> bool:
    result = await session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id,
    )
    db_file_meta = result.first()
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
    is_user: bool
) -> DBMessage:
    new_message = DBMessage(
        user_id=user_id,
        file_id=file_id,
        content=content,
        is_user_message=is_user
    )

    session.add(new_message)
    await session.flush()

    return new_message
    
    
async def get_messages(
    session: AsyncSession,
    user_id: UUID,
    file_id: UUID
) -> list[DBMessage] | None:
    result = await session.query(DBMessage).filter(
        DBMessage.user_id == user_id,
        DBMessage.file_id == file_id
    ).order_by(DBMessage.timestamp)
    return result.all()
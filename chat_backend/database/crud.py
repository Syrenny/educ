from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import *
from chat_backend.models import FileMeta


logger = logging.getLogger(__name__)
        
        
def list_file_meta(
    session: Session,
    user_id: UUID
) -> list[DBFileMeta]:
    return session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
    ).all()
        
        
def add_file_meta(
    session: Session,
    user_id: UUID,
    filename: str
    ) -> DBFileMeta:
    file_meta = DBFileMeta(
        user_id=user_id,
        filename=filename,
    )
    session.add(file_meta)
    
    session.flush()
    
    return file_meta


def find_file_meta(
    session: Session,
    user_id: UUID,
    file_id: UUID
) -> None | DBFileMeta:
    return session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id
    ).first()


def delete_file_meta(
    session: Session,
    user_id: UUID,
    file_id: UUID,
    ) -> None | DBFileMeta:    
    if file_meta := find_file_meta(session, user_id, file_id):
        session.delete(file_meta)

    return file_meta


def create_user(
    session: Session, 
    email: str, 
    password: str
    ) -> DBUser | None:
    """Создает нового пользователя."""
    try:
        user = DBUser(email=email, password=password)
        session.add(user)
        return user
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Ошибка при создании пользователя (IntegrityError): {e}")
        raise
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise


def get_user_by_email(
    session: Session, 
    email: str
    ) -> DBUser | None:
    """Возвращает пользователя по email, или None, если пользователь не найден."""
    return session.query(DBUser).filter(DBUser.email == email).first()


def create_token(
    session: Session, 
    user_id: UUID,
    token: str
    ) -> DBToken:
    """Создает токен для пользователя."""
    try:
        existing_token = session.query(
            DBToken).filter_by(user_id=user_id).first()

        if existing_token:
            existing_token.token = token
        else:
            existing_token = DBToken(user_id=user_id, token=token)
            session.add(existing_token)

        return existing_token
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при создании токена: {e}")
        raise


def save_file_chunks(
    session: Session,
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
        session.rollback()
        logger.error(f"Ошибка при сохранении чанков: {e}")
        raise


def find_file_chunks(
    session: Session,
    query: str,
    user_id: UUID,
    file_id: UUID
) -> list[DBChunk]:
    """Ищет чанки с помощью pg_trgm."""
    try:
        return session.query(DBChunk).filter(
            DBChunk.user_id == user_id,
            DBChunk.file_id == file_id,
            DBChunk.chunk_text.op('~')(query)
        ).all()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске чанков: {e}")
        return []


def delete_file_chunks(
    session: Session,
    user_id: UUID,
    filename: str,
    file_id: UUID
) -> None:
    """Удаляет чанки, связанные с файлом пользователя."""
    try:
        session.query(DBChunk).filter_by(
            user_id=user_id,
            filename=filename,
            file_id=file_id
        ).delete(synchronize_session=False)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при удалении чанков: {e}")
        raise
    
    
def set_indexed(
    session: Session,
    user_id: UUID,
    file_id: UUID,
    ) -> bool:
    db_file_meta = session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id,
    ).first()
    if db_file_meta:
        db_file_meta.is_indexed = True
        return True
    return False


def is_indexed(
    session: Session,
    user_id: UUID,
    file_id: UUID,
) -> bool | None:
    db_file_meta = find_file_meta(
        session=session,
        user_id=user_id,
        file_id=file_id
    )
    if db_file_meta is None:
        return None
    return db_file_meta.is_indexed

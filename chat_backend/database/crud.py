import logging

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import *
from chat_backend.models import FileMeta


logger = logging.getLogger(__name__)
        
        
def list_file_meta(
    session: Session,
    user_id: int
) -> list[DBFileMeta]:
    return session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
    ).all()
        
        
def add_file_meta(
    session: Session,
    user_id: int,
    filename: str
    ) -> DBFileMeta:
    file_meta = DBFileMeta(
        user_id=user_id,
        filename=filename,
        file_id=DBFileMeta.generate_file_id(filename)
    )
    session.add(file_meta)
    
    return file_meta


def find_file_meta(
    session: Session,
    user_id: int,
    file_id: str
) -> None | DBFileMeta:
    return session.query(DBFileMeta).filter(
        DBFileMeta.user_id == user_id,
        DBFileMeta.file_id == file_id
    ).first()


def delete_file_meta(
    session: Session,
    user_id: int,
    file_id: str,
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
    user_id: int, 
    token: str
    ) -> DBToken:
    """Создает токен для пользователя."""
    try:
        existing_token = session.query(
            DBToken).filter_by(user_id=user_id).first()

        if existing_token:
            existing_token.token = token  # Обновляем токен
        else:
            existing_token = DBToken(user_id=user_id, token=token)
            session.add(existing_token)  # Создаем новый

        return existing_token
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при создании токена: {e}")
        raise


def save_file_chunks(
    session: Session, 
    user_id: int, 
    meta: FileMeta,
    chunks: list[str]
    ) -> None:
    """Сохраняет чанки в БД и обновляет FTS-индекс."""
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
    user_id: int,
    file_id: str
) -> list[DBChunk]:
    """Ищет чанки по тексту внутри файла пользователя с использованием FTS в PostgreSQL."""
    try:
        result = session.execute(
            text("""
                SELECT id FROM chunks
                WHERE user_id = :user_id 
                AND file_id = :file_id 
                AND to_tsvector('english', chunk_text) @@ plainto_tsquery('english', :query)
            """),
            {"user_id": user_id, "file_id": file_id, "query": query}
        )

        row_ids = [row[0] for row in result.fetchall()]

        if not row_ids:
            return []

        return session.query(DBChunk).filter(DBChunk.id.in_(row_ids)).all()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске чанков: {e}")
        return []


def delete_file_chunks(
    session: Session, 
    user_id: int, 
    filename: str,
    file_id: str,
    ) -> None:
    """Удаляет все чанки, связанные с файлом пользователя, и обновляет FTS-индекс."""
    try:
        chunk_ids = session.query(DBChunk.id).filter(
            DBChunk.user_id == user_id,
            DBChunk.file_id == file_id,
            DBChunk.filename == filename
        ).all()

        if chunk_ids:
            chunk_ids = [cid[0] for cid in chunk_ids]
            session.query(DBChunk).filter(DBChunk.id.in_(
                chunk_ids)).delete(synchronize_session=False)
            session.execute(text("DELETE FROM fts_chunks WHERE rowid IN :ids"), {"ids": tuple(chunk_ids)})
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при удалении чанков: {e}")
        raise
    
    
def set_indexed(
    session: Session,
    user_id: int,
    file_id: str,
    status: bool
    ) -> bool:
    file_meta = session.query(DBFileMeta).filter(
        DBChunk.user_id == user_id,
        DBChunk.file_id == file_id,
    ).first()
    if file_meta:
        file_meta.is_indexed = status
        return True
    return False
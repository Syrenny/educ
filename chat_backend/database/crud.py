import logging

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .models import DBUser, DBToken, DBChunk


logger = logging.getLogger(__name__)


def create_user(
    session: Session, 
    email: str, 
    password: str
    ) -> DBUser | None:
    """Создает нового пользователя."""
    try:
        user = DBUser(email=email, password=password)
        session.add(user)
        session.commit()
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

        session.commit()
        return existing_token
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при создании токена: {e}")
        raise


def save_chunks(
    session: Session, 
    user_id: int, 
    filename: str, 
    chunks: list[str]
    ) -> None:
    """Сохраняет чанки в БД и обновляет FTS-индекс."""
    try:
        chunk_objects = [
            DBChunk(user_id=user_id, filename=filename, chunk_text=chunk)
            for chunk in chunks
        ]
        session.bulk_save_objects(chunk_objects)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при сохранении чанков: {e}")
        raise


def find_chunks(
    session: Session, 
    query: str, 
    user_id: int, 
    filename: str
    ) -> list[DBChunk]:
    """Ищет чанки по тексту внутри файла пользователя с использованием FTS."""
    try:
        return session.query(DBChunk).filter(
            DBChunk.user_id == user_id,
            DBChunk.filename == filename,
            DBChunk.id.in_(
                session.query(text("rowid")).from_statement(
                    text("SELECT rowid FROM fts_chunks WHERE fts_chunks MATCH :query")
                ).params(query=query)
            )
        ).all()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при поиске чанков: {e}")
        return []


def delete_chunks(
    session: Session, 
    user_id: int, 
    filename: str
    ) -> None:
    """Удаляет все чанки, связанные с файлом пользователя, и обновляет FTS-индекс."""
    try:
        chunk_ids = session.query(DBChunk.id).filter(
            DBChunk.user_id == user_id,
            DBChunk.filename == filename
        ).all()

        if chunk_ids:
            chunk_ids = [cid[0] for cid in chunk_ids]
            session.query(DBChunk).filter(DBChunk.id.in_(
                chunk_ids)).delete(synchronize_session=False)
            session.execute(text("DELETE FROM fts_chunks WHERE rowid IN :ids"), {"ids": tuple(chunk_ids)})
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка при удалении чанков: {e}")
        raise

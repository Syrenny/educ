from datetime import datetime

import sqlalchemy as db
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    token = relationship("DBToken", back_populates="user")
    chunks = relationship("DBChunk", back_populates="user",
                          cascade="all, delete-orphan")


class DBToken(Base):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    user = relationship("DBUser", back_populates="token")


class DBChunk(Base):
    __tablename__ = "chunks"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    user = relationship("DBUser", back_populates="chunks")


def update_fts_after_insert_update(mapper, connection, target):
    """Обновляет FTS-индекс после вставки или обновления."""
    connection.execute(
        db.text("INSERT INTO fts_chunks (rowid, chunk_text) VALUES (:id, :text) "
             "ON CONFLICT(rowid) DO UPDATE SET chunk_text=excluded.chunk_text"),
        {"id": target.id, "text": target.chunk_text}
    )


def update_fts_after_delete(mapper, connection, target):
    """Удаляет запись из FTS-индекса после удаления чанка."""
    connection.execute(
        db.text("DELETE FROM fts_chunks WHERE rowid = :id"),
        {"id": target.id}
    )
    
    
# Подключаем события к DBChunk
db.event.listen(DBChunk, "after_insert", update_fts_after_insert_update)
db.event.listen(DBChunk, "after_update", update_fts_after_insert_update)
db.event.listen(DBChunk, "after_delete", update_fts_after_delete)

import uuid
from datetime import datetime

import sqlalchemy as db
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

from chat_backend.models import Action

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    token = relationship("DBToken", back_populates="user", uselist=False)
    chunks = relationship("DBChunk", back_populates="user",
                          cascade="all, delete-orphan")
    files_meta = relationship(
        "DBFileMeta", back_populates="user", cascade="all, delete-orphan")
    messages = relationship(
        "DBMessage", back_populates="user", cascade="all, delete-orphan")



class DBToken(Base):
    __tablename__ = "tokens"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    token = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = relationship("DBUser", back_populates="token")


class DBFileMeta(Base):
    __tablename__ = "file_meta"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = db.Column(UUID(as_uuid=True), unique=True,
                        nullable=False, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    is_indexed = db.Column(db.Boolean, default=False)

    user = relationship("DBUser", back_populates="files_meta")
    chunks = relationship(
        "DBChunk", back_populates="file_meta", cascade="all, delete-orphan")
    messages = relationship(
        "DBMessage", back_populates="file_meta", cascade="all, delete-orphan")


message_chunk_association = db.Table(
    "message_chunk_association",
    db.Column(
        "message_id", 
        UUID(as_uuid=True),
        db.ForeignKey("messages.id"), 
        primary_key=True
    ),
    db.Column(
        "chunk_id", 
        UUID(as_uuid=True),
        db.ForeignKey("chunks.id"), 
        primary_key=True
    )
)


class DBMessage(Base):
    __tablename__ = "messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "file_meta.file_id"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    action = db.Column(db.Enum(Action, name="action_type"),
                       nullable=False, default=None)
    snippet = db.Column(db.Text, nullable=True, default=None)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_user_message = db.Column(db.Boolean, nullable=False)

    context = relationship(
        "DBChunk",
        secondary=message_chunk_association,
        backref="messages",
        cascade="all, delete",
    )
    
    file_meta = relationship("DBFileMeta", back_populates="messages")
    user = relationship("DBUser", back_populates="messages")


class DBChunk(Base):
    __tablename__ = "chunks"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "file_meta.file_id"), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    file_meta = relationship("DBFileMeta", back_populates="chunks")
    user = relationship("DBUser", back_populates="chunks")
    
    embedding = db.Column(Vector(1024))

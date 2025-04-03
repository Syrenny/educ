from sqlalchemy.schema import DDL
import uuid
from datetime import datetime

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR, JSONB
from sqlalchemy.orm import relationship, declarative_base

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
    metadata = db.Column(JSONB, nullable=True)

    user = relationship("DBUser", back_populates="files_meta")
    chunks = relationship(
        "DBChunk", back_populates="file_meta", cascade="all, delete-orphan")


class DBChunk(Base):
    __tablename__ = "chunks"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        "users.id"), nullable=False)
    filename = db.Column(db.String, nullable=False)
    file_id = db.Column(UUID(as_uuid=True), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    search_vector = db.Column(TSVECTOR)

    file_meta = relationship("DBFileMeta", back_populates="chunks")
    user = relationship("DBUser", back_populates="chunks")


db.event.listen(
    DBChunk.__table__, 'after_create',
    DDL("CREATE INDEX chunks_fts_idx ON chunks USING GIN (search_vector);")
)


def update_search_vector(mapper, connection, target):
    target.search_vector = db.func.to_tsvector("russian", target.chunk_text)


db.event.listen(DBChunk, "before_insert", update_search_vector)
db.event.listen(DBChunk, "before_update", update_search_vector)

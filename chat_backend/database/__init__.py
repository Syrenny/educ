import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from chat_backend.security import create_user, UserModel
from chat_backend.settings import settings
from .models import Base


def create_default_user(session: Session) -> None:
    """Creates a default admin user."""
    user = UserModel(
        email=settings.default_admin_email,
        password=settings.default_admin_password
    )
    create_user(
        session, 
        email=user.email,
        password=user.password
    )


def create_session():
    DATABASE_URL = "sqlite:///local.db"

    engine = db.create_engine(DATABASE_URL, connect_args={
                              "check_same_thread": False})

    Base.metadata.create_all(engine)

    # Create FTS5 table for full-text search
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(chunk_text)")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    
    if settings.debug:
        create_default_user(session)

    return session

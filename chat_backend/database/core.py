from contextlib import contextmanager

import sqlalchemy as db
from sqlalchemy.orm import Session, sessionmaker

from chat_backend.security import UserModel, hash_password
from chat_backend.settings import settings
from .models import Base
from .crud import create_user, get_user_by_email


def create_default_user(session: Session) -> None:
    """Creates a default admin user."""
    user = UserModel(
        email=settings.default_admin_email.get_secret_value(),
        password=settings.default_admin_password.get_secret_value()
    )
    create_user(
        session,
        email=user.email,
        password=hash_password(user.password)
    )


def init_db():
    engine = db.create_engine(
        settings.sqlalchemy_url, 
        pool_pre_ping=True
    )
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(
            db.text("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        )

    Base.metadata.create_all(engine)
    
    with engine.connect() as connection:
        connection.execute(
            db.text(
                'CREATE INDEX IF NOT EXISTS chunk_idx ON chunks USING GIN (chunk_text gin_trgm_ops);')
        )

    session_factory = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )

    if settings.env in ["DEBUG", "TEST"]:
        session = session_factory()
        try:
            if get_user_by_email(
                session, email=settings.default_admin_email.get_secret_value()
            ) is None:
                create_default_user(session)
                session.commit()
        finally:
            session.close()

    return session_factory


if settings.env != "TEST":
    SessionLocal = init_db()


@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

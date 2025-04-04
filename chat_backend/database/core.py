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
    if settings.mode == "TEST":
        # source: https://github.com/ArjanCodes/examples/blob/main/2023/apitesting/test_api.py
        engine = db.create_engine(
            "duckdb:///:memory:",
            connect_args={
                'read_only': False,
                'config': {
                    'memory_limit': '500mb'
                }
            }
        )
    else:
        engine = db.create_engine(
            f"sqlite:///{settings.sqlite_db_path}",
            connect_args={"check_same_thread": False}
        )

    Base.metadata.create_all(engine)

    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks 
USING fts5(chunk_text, user_id UNINDEXED, file_id UNINDEXED);
            """
        )

    session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)

    if settings.mode in ["DEBUG", "TEST"]:
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

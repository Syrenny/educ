import sqlalchemy as db
from sqlalchemy.orm import Session, sessionmaker

from chat_backend.security import UserModel, hash_password
from chat_backend.settings import settings
from .models import Base
from .crud import *


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


if settings.mode == "TEST":
    # source: https://github.com/ArjanCodes/examples/blob/main/2023/apitesting/test_api.py
    engine = db.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=db.StaticPool,
    )
else:
    engine = db.create_engine(
        "sqlite:///local.db",
        connect_args={"check_same_thread": False}
    )

Base.metadata.create_all(engine)

with engine.connect() as conn:
    conn.exec_driver_sql(
        "CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(chunk_text)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


if settings.mode in ["DEBUG", "TEST"]:
    session = next(get_db())
    if get_user_by_email(
        session,
        email=settings.default_admin_email.get_secret_value()
    ) is None:
        create_default_user(session)
        session.commit()      

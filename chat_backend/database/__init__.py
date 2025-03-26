import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from chat_backend.settings import settings
from .models import DBUser, DBChunk, Base


def manage_default_user(session: Session):
    """Creates a default admin user if in debug mode, or deletes it if not in debug mode."""
    default_admin_email = settings.default_admin_email
    default_admin_password = settings.default_admin_password

    existing_user = session.query(DBUser).filter_by(
        email=default_admin_email).first()

    if settings.debug:
        if existing_user is None:
            session.add(DBUser(email=default_admin_email,
                        password=default_admin_password))
            session.commit()
    else:
        if existing_user:
            session.delete(existing_user)
            session.commit()


def create_session():
    DATABASE_URL = "sqlite:///local.db"

    engine = db.create_engine(DATABASE_URL, connect_args={
                              "check_same_thread": False})

    db.event.listen(DBChunk, 'after_insert', DBChunk.update_fts)
    db.event.listen(DBChunk, 'after_update', DBChunk.update_fts)

    Base.metadata.create_all(engine)

    # Create FTS5 table for full-text search
    with engine.connect() as conn:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(chunk_text)")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    manage_default_user(session)

    return session

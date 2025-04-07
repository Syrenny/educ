import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from chat_backend.database.crud import create_user, create_token
from chat_backend.database.models import Base
from chat_backend.settings import settings
from chat_backend.security import UserModel, hash_password, generate_access_token


@pytest.fixture(scope="session", autouse=True)
def check_test_env():
    assert settings.env == "TEST"
    
    
@pytest.fixture(scope="function")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        postgres.start()
        yield postgres


@pytest.fixture(scope="function")
def db_session(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(
            text("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        )

    Base.metadata.create_all(engine)

    with engine.connect() as connection:
        connection.execute(
            text(
                'CREATE INDEX IF NOT EXISTS chunk_idx ON chunks USING GIN (chunk_text gin_trgm_ops);')
        )

    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    user = UserModel(
        email=settings.default_admin_email.get_secret_value(),
        password=settings.default_admin_password.get_secret_value()
    )
    db_user = create_user(
        session=session,
        email=user.email,
        password=hash_password(user.password)
    )

    session.flush()

    token = generate_access_token(db_user)
    create_token(
        session=session,
        user_id=db_user.id,
        token=token
    )
    session.commit()

    yield session, db_user.id

    session.rollback()
    session.close()

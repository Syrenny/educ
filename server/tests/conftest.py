import pytest
from testcontainers.postgres import PostgresContainer

from server.config import EnvMode, config, secrets
from server.database import get_user_by_email, session_manager


@pytest.fixture(scope="session", autouse=True)
def check_test_env():
    assert config.env == EnvMode.test


# Source: https://github.com/testcontainers/testcontainers-python/issues/263
@pytest.fixture(scope="function")
def postgres_url():
    with PostgresContainer("pgvector/pgvector:pg15", driver="asyncpg") as postgres:
        postgres.start()
        print(f"Connecting to test DB at: {postgres.get_connection_url()}")
        yield postgres.get_connection_url()


@pytest.fixture(scope="function")
async def db_session(postgres_url):
    await session_manager.init_db(postgres_url)

    async with session_manager.session() as session:
        db_user = await get_user_by_email(
            session=session, email=secrets.default_admin_email.get_secret_value()
        )
        yield session, db_user.id
    await session_manager.close()

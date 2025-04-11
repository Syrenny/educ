import contextlib

import pytest
from testcontainers.postgres import PostgresContainer

from chat_backend.database import get_user_by_email, session_manager
from chat_backend.settings import settings


@pytest.fixture(scope="session", autouse=True)
def check_test_env():
    assert settings.env == "TEST"
    

# Source: https://github.com/testcontainers/testcontainers-python/issues/263
# @pytest.fixture(scope="function")
@contextlib.contextmanager
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        # postgres.driver = "asyncpg"
        postgres.start()
        print("======PG-LOGS======")
        print(postgres.get_connection_url())
        yield postgres
        session_manager.close()


@pytest.fixture(scope="function")
async def db_session():
    with postgres_container() as pg:
        await session_manager.init_db(pg.get_connection_url())
        async with session_manager.session() as session:
            db_user = await get_user_by_email(
                session=session,
                email=settings.default_admin_email.get_secret_value()
            )
            return session, db_user.id


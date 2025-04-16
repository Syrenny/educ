
import asyncio
import contextlib

import sqlalchemy as db
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine, create_async_engine

from chat_backend.security import UserModel, hash_password, generate_access_token
from chat_backend.settings import settings
from .models import Base
from .crud import create_user, get_user_by_email, create_token


class NotInitializedError(Exception):
    """Raised when database session manager is used before initialization."""


# Reference: https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e
class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None
        
    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise NotInitializedError("Engine is not initialized.")
        return self._engine

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise NotInitializedError("Sessionmaker is not initialized.")
        return self._sessionmaker

    async def init_db(self, url: str) -> None:
        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        await self.__create_schema()

        if settings.env in ["DEBUG", "TEST"]:
            await self.__create_default_user()
                
    async def __create_schema(self):
        async with self.engine.connect() as conn:
            conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(db.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(
                db.text(
                    'CREATE INDEX IF NOT EXISTS chunk_idx ON chunks USING GIN (chunk_text gin_trgm_ops);')
            )
            
    async def __create_default_user(self):
        user_model = UserModel(
            email=settings.default_admin_email.get_secret_value(),
            password=settings.default_admin_password.get_secret_value()
        )
        async with self.sessionmaker() as session:
            user = await get_user_by_email(
                session, 
                email=settings.default_admin_email.get_secret_value()
            )
            if user is None:
                db_user = await create_user(
                    session,
                    email=user_model.email,
                    password=hash_password(user_model.password)
                )
                await session.flush()
                token = generate_access_token(db_user)
                await create_token(
                    session=session,
                    user_id=db_user.id,
                    token=token
                )
                await session.commit()
    
    async def close(self):
        if self._engine is not None:
            await self.engine.dispose()
            self._engine = None
            self._sessionmaker = None
    
    
    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
        

session_manager = DatabaseSessionManager()
    

async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
            yield session

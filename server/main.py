# source: https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/api_server.py#L25
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.auth import router as auth_router
from server.api.completions import router as completions_router
from server.api.files import router as files_router
from server.api.health import router as health_router
from server.api.history import router as history_router
from server.config import EnvMode, config, secrets
from server.database import session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.env is not EnvMode.test:
        await session_manager.init_db(secrets.sqlalchemy_url.get_secret_value())
    yield
    await session_manager.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://client",
        "http://localhost:3000",
        "http://client:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = "/api"
app.include_router(completions_router, prefix=prefix)
app.include_router(files_router, prefix=prefix)
app.include_router(auth_router, prefix=prefix)
app.include_router(history_router, prefix=prefix)
app.include_router(health_router, prefix=prefix)

# source: https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/api_server.py#L25
from functools import lru_cache
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_community.cache import SQLiteCache
from langchain_core.rate_limiters import InMemoryRateLimiter

from chat_backend.api.auth import router as auth_router
from chat_backend.settings import settings
from chat_backend.api.files import router as files_router
from chat_backend.api.completions import router as completions_router
from chat_backend.api.history import router as history_router 

    
@lru_cache(maxsize=None)
def get_langchain_openai_instance():
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=settings.llm_requests_per_second,
        check_every_n_seconds=settings.llm_check_every_n_seconds,
        max_bucket_size=settings.llm_max_bucket_size,
    )
    
    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        # Always a good idea to use Cache
        cache=SQLiteCache(settings.llm_cache_path),
        rate_limiter=rate_limiter,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.langchain_openai_client = get_langchain_openai_instance()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(completions_router)
app.include_router(files_router)
app.include_router(auth_router)
app.include_router(history_router)


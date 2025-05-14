from functools import cache

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.cache import SQLiteCache
from langchain_core.embeddings.embeddings import Embeddings as LangchainEmbeddings
from langchain_core.language_models.llms import LLM
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from loguru import logger

from server.config import config, secrets


@cache
def get_langchain_llm(model_name: str | None = None) -> LLM:
    if model_name is None:
        model_name = config.llm_model_name
    logger.info(f"Init model {model_name}")
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=config.llm_requests_per_second,
        check_every_n_seconds=config.llm_check_every_n_seconds,
        max_bucket_size=config.llm_max_bucket_size,
    )
    return ChatOpenAI(
        model=model_name,
        api_key=secrets.llm_api_key.get_secret_value(),
        base_url=config.llm_api_base,
        rate_limiter=rate_limiter,
        cache=SQLiteCache(),
        streaming=True,
    )


@cache
def get_langchain_embeddings() -> LangchainEmbeddings:
    # Configure the embeddings model and cache
    underlying_embeddings = HuggingFaceEmbeddings(
        model_name=config.embeddings_model_name,
        model_kwargs={"trust_remote_code": True},
        encode_kwargs={"batch_size": 10},
    )

    store = LocalFileStore(config.embeddings_cache_path)

    return CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings, store, namespace=config.embeddings_model_name
    )

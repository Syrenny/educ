from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain.storage import LocalFileStore
from langchain_community.cache import SQLiteCache
from langchain.embeddings import CacheBackedEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.language_models.llms import LLM as LangchainLLM
from langchain_core.embeddings.embeddings import Embeddings as LangchainEmbeddings


from chat_backend.settings import settings


@lru_cache(maxsize=None)
def get_langchain_llm() -> LangchainLLM:
    vsegpt_rate_limiter = InMemoryRateLimiter(
        requests_per_second=1,
        check_every_n_seconds=1,
        max_bucket_size=1,
    )
    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        # Always a good idea to use Cache
        cache=SQLiteCache("./benchmark/data/cache/openai_cache.db"),
        rate_limiter=vsegpt_rate_limiter,
    )


@lru_cache(maxsize=None)
def get_langchain_embeddings() -> LangchainEmbeddings:
    # Configure the embeddings model and cache
    underlying_embeddings = HuggingFaceEmbeddings(
        model_name=settings.benchmark_embedding_model,
        encode_kwargs={
            "batch_size": 10
        }
    )

    store = LocalFileStore(settings.embeddings_cache_path)

    return CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings,
        store,
        namespace=settings.benchmark_embedding_model
    )

import os

from pathlib import Path

from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    mode: str
     
    # Cache store
    embeddings_cache_path: str
      
    # LLM configuration
    llm_model_name: str
    llm_api_key: SecretStr
    llm_api_base: str
    llm_cache_path: str
    
    # Rate limiter
    llm_requests_per_second: int
    llm_check_every_n_seconds: int
    llm_max_bucket_size: int
    
    # Benchmark
    dataset_checkpoint: str
    ragas_api_key: SecretStr
    benchmark_embedding_model: str
    benchmark_llm_model_name: str
    benchmark_llm_api_key: SecretStr
    benchmark_llm_api_base: str
    benchmark_n_samples: int
    
    # s3
    s3_endpoint: str
    s3_access_key: SecretStr
    s3_secret_key: SecretStr
    s3_bucket: str
    s3_region: str
    
    # jwt
    jwt_secret_key: SecretStr
    jwt_algorithm: str
    jwt_token_expires_minutes: int
    
    # default user
    default_admin_email: SecretStr
    default_admin_password: SecretStr
    
    # pdf-saving
    file_storage_path: Path
    max_files_per_user: int
    max_file_size: int
    
    # Chunker
    chunker_name: str
    
    
class TestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env.test", env_file_encoding="utf-8")


if os.getenv("MODE", "DEFAULT") == "TEST":
    settings = TestSettings()
else:
    settings = Settings()

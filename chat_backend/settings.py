from pydantic_settings import BaseSettings


class Settings(BaseSettings):  
    # Cache store
    embeddings_cache_path: str
      
    # LLM configuration
    llm_model_name: str
    llm_api_key: str
    llm_api_base: str
    llm_cache_path: str
    
    # Rate limiter
    llm_requests_per_second: int
    llm_check_every_n_seconds: int
    llm_max_bucket_size: int
    
    # Benchmark
    dataset_checkpoint: str
    ragas_api_key: str
    benchmark_embedding_model: str
    benchmark_llm_model_name: str
    benchmark_llm_api_key: str
    benchmark_llm_api_base: str
    benchmark_n_samples: int
    
    # s3
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str
    
    # jwt
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_token_expires_minutes: int
    
    class Config:
        env_file = ".env"
        
        
settings = Settings()
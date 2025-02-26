from pydantic_settings import BaseSettings


class Settings(BaseSettings):  
    # Cache store
    embeddings_cache_path: str
      
    # LLM configuration
    llm_model_name: str
    llm_api_key: str
    llm_api_base: str
    
    # Benchmark
    dataset_checkpoint: str
    ragas_api_key: str
    benchmark_embedding_model: str
    benchmark_llm_model_name: str
    benchmark_llm_api_key: str
    benchmark_llm_api_base: str
    benchmark_n_samples: int
    
    class Config:
        env_file = ".env"
        
        
settings = Settings()
from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    # LLM configuration
    llm_model_name: str
    llm_api_key: str
    llm_api_base: str
    
    # Benchmark
    benchmark_embedding_model: str
    benchmark_llm_model_name: str
    benchmark_llm_api_key: str
    benchmark_llm_api_base: str
    benchmark_n_samples: int
    
    class Config:
        env_file = ".env"
        
        
settings = Settings()
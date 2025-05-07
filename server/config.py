from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvMode(str, Enum):
    dev = "DEV"
    test = "TEST"
    prod = "PROD"


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_api_key: SecretStr
    jwt_secret_key: SecretStr

    # Set up default user (admin)
    default_admin_email: SecretStr
    default_admin_password: SecretStr

    # Full URL to connect DB
    sqlalchemy_url: SecretStr

    # Secret key for temporary url generating
    sign_secret_key: SecretStr


class Config(BaseModel):
    # DEBUG/TEST/PROD
    env: EnvMode

    # Cache store for embeddings
    embeddings_model_name: str
    embeddings_cache_path: str

    # LLM API configuration
    llm_model_name: str
    llm_api_base: str

    # Rate limiter for LLM API
    llm_requests_per_second: int
    llm_check_every_n_seconds: int
    llm_max_bucket_size: int

    # JWT for protected routes
    jwt_algorithm: str
    jwt_token_expires_minutes: int

    # Local file storage settings
    file_storage_path: Path
    max_files_per_user: int
    max_file_size: int


def load_config() -> Config:
    with open("./server/config.yaml") as f:
        data = yaml.safe_load(f)
    data["env"] = EnvMode(data["env"])
    return Config(**data)


config = load_config()
secrets = Secrets()

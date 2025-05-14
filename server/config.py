from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic.types import SecretStr
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvMode(str, Enum):
    dev = "DEV"
    test = "TEST"
    prod = "PROD"


class Secrets(BaseSettings):
    model_config = SettingsConfigDict(env_file="docker/.env", env_file_encoding="utf-8")

    llm_api_key: SecretStr
    jwt_secret_key: SecretStr

    # Set up default user (admin)
    default_admin_email: SecretStr
    default_admin_password: SecretStr

    # Secret key for temporary url generating
    sign_secret_key: SecretStr

    # PG settings
    postgres_db: SecretStr
    postgres_user: SecretStr
    postgres_password: SecretStr

    @computed_field
    def sqlalchemy_url(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user.get_secret_value(),
            password=self.postgres_password.get_secret_value(),
            host="educ_pg",
            port=5432,
            path=self.postgres_db.get_secret_value(),
        )


class Config(BaseModel):
    # DEBUG/TEST/PROD
    env: EnvMode

    # Cache store for embeddings
    embeddings_model_name: str
    embeddings_cache_path: str

    # LLM API configuration
    llm_model_name: str
    llm_api_base: str

    # LLM cache settings
    enable_llm_cache: bool

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

    # Grobid connection
    grobid_base: str


def load_config() -> Config:
    with open("./server/config.yaml") as f:
        raw = yaml.safe_load(f)

    env = EnvMode(raw["env"])

    def resolve_env_value(val):
        if isinstance(val, dict) and env.value in val:
            return val[env.value]
        return val

    resolved = {k: resolve_env_value(v) for k, v in raw.items()}
    resolved["env"] = env

    return Config(**resolved)


config = load_config()
secrets = Secrets()

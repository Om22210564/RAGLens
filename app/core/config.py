from functools import lru_cache
from pathlib import Path

# Dsn Data Source Name validation for structure of database and redis urls
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    database_url: PostgresDsn = PostgresDsn("postgresql+asyncpg://rag:rag@localhost:5432/rag")
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    max_request_bytes: int = 1_048_576
    max_upload_bytes: int = 26_214_400
    storage_directory: Path = Path("data/uploads")
    chunk_target_tokens: int = 500
    chunk_overlap_tokens: int = 75
    max_query_characters: int = 4_000
    retrieval_candidate_count: int = 30
    retrieval_top_k: int = 8
    context_token_budget: int = 2_500
    dev_auth_enabled: bool = True


# lru_cache() function is used to cache the results of function calls
@lru_cache
def get_settings() -> Settings:
    return Settings()

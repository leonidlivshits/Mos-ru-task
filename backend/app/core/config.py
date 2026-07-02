from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mos.ru Lost Items Demo"
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg_async://lost_items:lost_items_password@localhost:5432/lost_items_demo"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_embedding_dimensions: int = 384
    openrouter_http_referer: str = "http://localhost:8000"
    openrouter_app_title: str = "Mos.ru Lost Items Demo"
    telegram_bot_token: str = ""
    backend_api_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

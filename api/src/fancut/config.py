"""Runtime configuration, read from environment variables (prefix ``NK_``) or ``api/.env``."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NK_", env_file=".env", extra="ignore")

    environment: Literal["local", "test", "production"] = "local"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

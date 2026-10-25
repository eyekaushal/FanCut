"""Runtime configuration, read from environment variables (prefix ``NK_``) or ``api/.env``."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NK_", env_file=".env", extra="ignore")

    environment: Literal["local", "test", "production"] = "local"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]
    # Host headers the MCP endpoint accepts (DNS-rebinding protection stays on).
    # Add the deployed hostname in Azure, e.g. NK_MCP_ALLOWED_HOSTS='["api.example.net"]'.
    mcp_allowed_hosts: list[str] = ["localhost", "localhost:*", "127.0.0.1", "127.0.0.1:*"]

    # Microsoft Foundry model deployment (any OpenAI-compatible endpoint works).
    llm_endpoint: str | None = None
    llm_api_key: SecretStr | None = None
    llm_deployment: str | None = None

    # Print agent traces to the console (Application Insights is configured in Azure).
    trace_console: bool = False

    # Matchdays the Director is measured on when the Studio asks (``GET /evaluation``).
    evaluation_seeds: list[int] = [34, 35, 36, 37, 38, 39]

    # Azure AI Speech (the Foundry resource's key and region also work here).
    speech_region: str | None = None
    speech_key: SecretStr | None = None

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_endpoint and self.llm_api_key and self.llm_deployment)

    @property
    def speech_configured(self) -> bool:
        return bool(self.speech_region and self.speech_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()

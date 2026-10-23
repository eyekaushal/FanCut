import pytest

from fancut.config import Settings
from fancut.llm import LLMNotConfiguredError, chat_client, openai_v1_base_url


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://demo.openai.azure.com",
        "https://demo.openai.azure.com/",
        "https://demo.openai.azure.com/openai/v1/",
    ],
)
def test_endpoint_becomes_the_openai_v1_url(endpoint: str) -> None:
    assert openai_v1_base_url(endpoint).rstrip("/") == "https://demo.openai.azure.com/openai/v1"


def test_missing_settings_fail_loudly() -> None:
    settings = Settings(_env_file=None, llm_endpoint=None, llm_api_key=None, llm_deployment=None)  # type: ignore[call-arg]
    assert not settings.llm_configured
    with pytest.raises(LLMNotConfiguredError):
        chat_client(settings)

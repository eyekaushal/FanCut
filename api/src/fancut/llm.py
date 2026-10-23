"""The chat client every agent uses, built from configuration.

Microsoft Foundry exposes deployments through the OpenAI v1 API, so one client type
covers Foundry on Azure and Foundry Local alike; only the settings differ.
"""

from agent_framework.openai import OpenAIChatCompletionClient

from fancut.config import Settings


class LLMNotConfiguredError(RuntimeError):
    pass


def openai_v1_base_url(endpoint: str) -> str:
    """``https://x.openai.azure.com/`` -> ``https://x.openai.azure.com/openai/v1/``."""
    root = endpoint.rstrip("/")
    return root if root.endswith("/openai/v1") else f"{root}/openai/v1/"


def chat_client(settings: Settings) -> OpenAIChatCompletionClient:
    if not settings.llm_configured:
        raise LLMNotConfiguredError("Set NK_LLM_ENDPOINT, NK_LLM_API_KEY and NK_LLM_DEPLOYMENT")
    assert settings.llm_endpoint and settings.llm_api_key  # narrowed by llm_configured
    return OpenAIChatCompletionClient(
        model=settings.llm_deployment,
        api_key=settings.llm_api_key.get_secret_value(),
        base_url=openai_v1_base_url(settings.llm_endpoint),
    )

"""The language-model seam every agent talks through.

``FoundryModel`` runs each call as a named Microsoft Agent Framework agent (so every call
is traced under the agent's name). Tests use a scripted double with the same shape.
"""

from typing import Protocol, TypeVar

from agent_framework import Agent, ChatOptions
from agent_framework.openai import OpenAIChatCompletionClient
from pydantic import BaseModel

Structured = TypeVar("Structured", bound=BaseModel)


class LanguageModel(Protocol):
    async def text(self, agent: str, instructions: str, prompt: str) -> str: ...

    async def structured(
        self, agent: str, instructions: str, prompt: str, schema: type[Structured]
    ) -> Structured: ...


class FoundryModel:
    """A Microsoft Foundry deployment, called through Agent Framework agents."""

    def __init__(self, client: OpenAIChatCompletionClient) -> None:
        self._client = client

    async def text(self, agent: str, instructions: str, prompt: str) -> str:
        response = await Agent(self._client, instructions, name=agent).run(prompt)
        return response.text.strip()

    async def structured(
        self, agent: str, instructions: str, prompt: str, schema: type[Structured]
    ) -> Structured:
        runner = Agent(self._client, instructions, name=agent)
        response = await runner.run(prompt, options=ChatOptions(response_format=schema))
        if isinstance(response.value, schema):
            return response.value
        return schema.model_validate_json(response.text)

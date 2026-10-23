from collections.abc import Iterator
from typing import TypeVar

import pytest
from pydantic import BaseModel

from fancut.agents.broadcast import Beat, beats
from fancut.demo import ARJUN, MAYA
from fancut.matchday.matchday import Matchday

Structured = TypeVar("Structured", bound=BaseModel)


class ScriptedModel:
    """A stand-in for the language model: replies come from a script, in order."""

    def __init__(self, texts: list[str] | None = None, verdicts: list[BaseModel] | None = None):
        self._texts: Iterator[str] = iter(texts or [])
        self._structured: Iterator[BaseModel] = iter(verdicts or [])
        self.calls: list[str] = []

    async def text(self, agent: str, instructions: str, prompt: str) -> str:
        self.calls.append(agent)
        return next(self._texts)

    async def structured(
        self, agent: str, instructions: str, prompt: str, schema: type[Structured]
    ) -> Structured:
        self.calls.append(agent)
        reply = next(self._structured)
        assert isinstance(reply, schema)
        return reply


@pytest.fixture(scope="session")
def arjun_beats(matchday: Matchday) -> list[Beat]:
    return beats(matchday, ARJUN)


@pytest.fixture(scope="session")
def maya_beats(matchday: Matchday) -> list[Beat]:
    return beats(matchday, MAYA)

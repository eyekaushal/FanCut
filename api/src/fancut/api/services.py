"""Everything the HTTP and MCP layers share, created once per process."""

import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from fancut.agents.commentary import Commentary
from fancut.agents.model import FoundryModel, LanguageModel
from fancut.config import Settings
from fancut.demo import PROFILES
from fancut.llm import chat_client
from fancut.matchday.matchday import Matchday, build_matchday
from fancut.profile import FanProfile

if TYPE_CHECKING:
    from fancut.api.channel import ChannelSession

MAX_SESSIONS = 200  # the oldest channel is forgotten beyond this


class ProfileStore:
    """In-memory profiles, seeded with the demo fans."""

    def __init__(self) -> None:
        self._profiles: dict[str, FanProfile] = dict(PROFILES)

    def add(self, profile: FanProfile) -> str:
        profile_id = uuid.uuid4().hex[:12]
        self._profiles[profile_id] = profile
        return profile_id

    def get(self, profile_id: str) -> FanProfile | None:
        return self._profiles.get(profile_id)

    def demo(self) -> dict[str, FanProfile]:
        return {key: self._profiles[key] for key in PROFILES}


@dataclass
class Services:
    matchday: Matchday
    model: LanguageModel | None
    profiles: ProfileStore = field(default_factory=ProfileStore)
    sessions: "OrderedDict[str, ChannelSession]" = field(default_factory=OrderedDict)

    @property
    def commentary(self) -> Commentary:
        return Commentary(self.model)

    def remember(self, session: "ChannelSession") -> str:
        session_id = uuid.uuid4().hex[:12]
        self.sessions[session_id] = session
        while len(self.sessions) > MAX_SESSIONS:
            self.sessions.popitem(last=False)
        return session_id


def build_services(settings: Settings, matchday_seed: int = 34) -> Services:
    model = FoundryModel(chat_client(settings)) if settings.llm_configured else None
    return Services(matchday=build_matchday(matchday_seed), model=model)

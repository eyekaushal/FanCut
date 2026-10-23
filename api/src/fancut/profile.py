"""The ``profile.v1`` fan profile: everything that makes one fan's channel different."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "profile.v1"
MAX_FANTASY_SQUAD = 15


class Language(StrEnum):
    ENGLISH = "en"
    HINDI = "hi"  # Devanagari
    HINGLISH = "hinglish"  # Hindi in Latin script


class Depth(StrEnum):
    CASUAL = "casual"
    ANALYST = "analyst"


class FanProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: str = SCHEMA_VERSION
    name: str
    club_id: str | None = None
    player_ids: tuple[str, ...] = ()
    fantasy_squad: tuple[str, ...] = Field(default=(), max_length=MAX_FANTASY_SQUAD)
    captain_id: str | None = None
    language: Language = Language.ENGLISH
    depth: Depth = Depth.CASUAL

    @model_validator(mode="after")
    def _captain_in_squad(self) -> "FanProfile":
        if self.captain_id is not None and self.captain_id not in self.fantasy_squad:
            raise ValueError("captain must be in the fantasy squad")
        return self

    def cares_about_player(self, player_id: str) -> bool:
        return player_id in self.player_ids or player_id in self.fantasy_squad

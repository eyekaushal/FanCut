"""The ``event.v1`` data contract shared by the simulator, the drama engine and the API.

Coordinates are absolute metres on a 105 x 68 pitch. The home side always attacks
towards x = 105 and the away side towards x = 0 (no switch at half-time, which keeps
every consumer simple).
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

PITCH_LENGTH = 105.0
PITCH_WIDTH = 68.0
SCHEMA_VERSION = "event.v1"


class Side(StrEnum):
    HOME = "home"
    AWAY = "away"

    @property
    def opponent(self) -> "Side":
        return Side.AWAY if self is Side.HOME else Side.HOME


class Position(StrEnum):
    GK = "GK"
    DF = "DF"
    MF = "MF"
    FW = "FW"


class EventType(StrEnum):
    KICKOFF = "kickoff"
    PASS = "pass"
    CARRY = "carry"
    PRESSURE = "pressure"
    SHOT = "shot"
    SAVE = "save"
    GOAL = "goal"
    TACKLE = "tackle"
    INTERCEPTION = "interception"
    FOUL = "foul"
    CARD = "card"
    FREE_KICK = "free_kick"
    CORNER = "corner"
    OFFSIDE = "offside"
    SUBSTITUTION = "substitution"
    POSSESSION_CHANGE = "possession_change"
    HALF_TIME = "half_time"
    FULL_TIME = "full_time"


class Stakes(StrEnum):
    TITLE_RACE = "title_race"
    TOP_FOUR = "top_four"
    RELEGATION = "relegation"
    DERBY = "derby"
    MID_TABLE = "mid_table"


class Archetype(StrEnum):
    """The drama scenario a match was generated to exhibit (ground truth for evaluation)."""

    BASELINE = "baseline"
    DEAD_RUBBER = "dead_rubber"
    GOALLESS_THRILLER = "goalless_thriller"
    LATE_COMEBACK = "late_comeback"
    RED_CARD_CHAOS = "red_card_chaos"
    EARLY_BLOWOUT = "early_blowout"
    END_TO_END = "end_to_end"


class Verdict(StrEnum):
    WATCH = "watch"
    SKIM = "skim"
    SKIP = "skip"


Qualifier = str | int | float | bool


class Event(BaseModel):
    model_config = ConfigDict(frozen=True)

    match_id: str
    seq: int = Field(ge=0)
    t: float = Field(ge=0, description="Elapsed playing seconds since kickoff; always increases.")
    clock: float = Field(
        ge=0, description="Football clock in seconds: the second half restarts at 45:00."
    )
    period: int = Field(ge=1, le=2)
    type: EventType
    side: Side | None = None
    player_id: str | None = None
    x: float | None = Field(default=None, ge=0, le=PITCH_LENGTH)
    y: float | None = Field(default=None, ge=0, le=PITCH_WIDTH)
    end_x: float | None = Field(default=None, ge=0, le=PITCH_LENGTH)
    end_y: float | None = Field(default=None, ge=0, le=PITCH_WIDTH)
    outcome: bool | None = None
    xg: float | None = Field(default=None, ge=0, le=1)
    qualifiers: dict[str, Qualifier] = Field(default_factory=dict)

    @property
    def minute(self) -> int:
        """Displayed minute, e.g. 70 for the 70th minute (stoppage time continues counting)."""
        return int(self.clock // 60) + 1


class Player(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    number: int
    position: Position


class Team(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    short_name: str
    color: str
    strength: float = Field(gt=0, description="Relative quality; 1.0 is league average.")
    players: tuple[Player, ...]
    star_player_id: str

    @property
    def starters(self) -> tuple[Player, ...]:
        return self.players[:11]

    @property
    def bench(self) -> tuple[Player, ...]:
        return self.players[11:]


class MatchMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    match_id: str
    seed: int
    kickoff_utc: datetime
    home: Team
    away: Team
    stakes: Stakes
    archetype: Archetype

    def team(self, side: Side) -> Team:
        return self.home if side is Side.HOME else self.away


class Window(BaseModel):
    """A labelled span of match time, in seconds."""

    model_config = ConfigDict(frozen=True)

    start_t: float
    end_t: float
    reason: str


class GroundTruth(BaseModel):
    model_config = ConfigDict(frozen=True)

    decisive_windows: tuple[Window, ...]
    dramatic_windows: tuple[Window, ...]
    verdict: Verdict
    final_score: tuple[int, int]


class Match(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: str = SCHEMA_VERSION
    meta: MatchMeta
    events: tuple[Event, ...]
    truth: GroundTruth

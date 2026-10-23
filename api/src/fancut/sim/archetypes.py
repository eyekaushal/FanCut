"""Drama archetypes: how each scenario bends the simulation, and the check that proves it did.

The simulator stays the same for every match. An archetype only nudges *intensities*
(how hard each side attacks, how chaotic play is, how likely a red card is) and then
``accepts`` the finished match if the scenario really happened. The league builder
retries with the next seed until it does, so every labelled match is genuine.
"""

from collections.abc import Callable
from dataclasses import dataclass

from fancut.sim.labels import Summary
from fancut.sim.schema import Archetype, Side, Stakes
from fancut.sim.state import GameState

Intensity = Callable[[Side, GameState, Side], float]
"""(side, state, favourite) -> attacking multiplier; 1.0 is neutral."""


@dataclass(frozen=True)
class ArchetypeSpec:
    archetype: Archetype
    stakes: tuple[Stakes, ...]
    intensity: Intensity
    accepts: Callable[[Summary], bool]
    chaos: float = 0.0
    """Extra probability that any pass goes astray (end-to-end games are scrappy)."""
    red_card_boost: float = 1.0
    wide_strength_gap: bool = False


def _neutral(_side: Side, _state: GameState, _favourite: Side) -> float:
    return 1.0


def _subdued(_side: Side, _state: GameState, _favourite: Side) -> float:
    return 0.6


def _open(_side: Side, _state: GameState, _favourite: Side) -> float:
    return 1.45


def _late_surge(side: Side, state: GameState, _favourite: Side) -> float:
    if state.minute < 65:
        return 1.0
    margin = state.margin(side)
    if margin < 0:
        return 2.0
    return 0.7 if margin > 0 else 1.2


def _early_rout(side: Side, state: GameState, favourite: Side) -> float:
    if side is favourite:
        return 2.3 if state.minute < 45 else 1.0
    return 0.7


def _ten_men(side: Side, state: GameState, _favourite: Side) -> float:
    down = state.red_cards[side] - state.red_cards[side.opponent]
    if down > 0:
        return 0.75
    return 1.5 if down < 0 else 1.15


def _late_comeback(s: Summary) -> bool:
    home70, away70 = s.at_70
    home, away = s.final
    if home70 < away70:
        return home >= away
    if away70 < home70:
        return away >= home
    return False


SPECS: dict[Archetype, ArchetypeSpec] = {
    Archetype.BASELINE: ArchetypeSpec(
        Archetype.BASELINE,
        stakes=(Stakes.MID_TABLE, Stakes.TOP_FOUR, Stakes.RELEGATION),
        intensity=_neutral,
        accepts=lambda _: True,
    ),
    Archetype.DEAD_RUBBER: ArchetypeSpec(
        Archetype.DEAD_RUBBER,
        stakes=(Stakes.MID_TABLE,),
        intensity=_subdued,
        accepts=lambda s: sum(s.final) <= 1 and s.total_xg < 1.6 and not s.late_lead_change,
    ),
    Archetype.GOALLESS_THRILLER: ArchetypeSpec(
        Archetype.GOALLESS_THRILLER,
        stakes=(Stakes.TITLE_RACE, Stakes.DERBY, Stakes.TOP_FOUR),
        intensity=_open,
        accepts=lambda s: s.final == (0, 0) and s.total_xg >= 2.5,
    ),
    Archetype.LATE_COMEBACK: ArchetypeSpec(
        Archetype.LATE_COMEBACK,
        stakes=(Stakes.TITLE_RACE, Stakes.RELEGATION, Stakes.DERBY),
        intensity=_late_surge,
        accepts=_late_comeback,
    ),
    Archetype.RED_CARD_CHAOS: ArchetypeSpec(
        Archetype.RED_CARD_CHAOS,
        stakes=(Stakes.DERBY, Stakes.RELEGATION),
        intensity=_ten_men,
        accepts=lambda s: (
            any(m < 70 for m in s.red_card_minutes)
            and sum(s.final) >= 3
            and abs(s.final[0] - s.final[1]) <= 1
        ),
        red_card_boost=8.0,
    ),
    Archetype.EARLY_BLOWOUT: ArchetypeSpec(
        Archetype.EARLY_BLOWOUT,
        stakes=(Stakes.MID_TABLE, Stakes.TOP_FOUR),
        intensity=_early_rout,
        accepts=lambda s: abs(s.at_half[0] - s.at_half[1]) >= 3,
        wide_strength_gap=True,
    ),
    Archetype.END_TO_END: ArchetypeSpec(
        Archetype.END_TO_END,
        stakes=(Stakes.DERBY, Stakes.TITLE_RACE, Stakes.TOP_FOUR),
        intensity=_open,
        accepts=lambda s: sum(s.final) >= 4 and s.lead_changes >= 3,
        chaos=0.06,
    ),
}

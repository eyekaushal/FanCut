"""A fictional league: every club and player name is invented, none is real."""

import random
from dataclasses import dataclass

from fancut.sim.schema import Player, Position, Team

# 4-3-3: GK, four defenders, three midfielders, three forwards, then five substitutes.
_FORMATION = (
    (Position.GK, 1),
    (Position.DF, 4),
    (Position.MF, 3),
    (Position.FW, 3),
)
_BENCH = (Position.GK, Position.DF, Position.MF, Position.MF, Position.FW)

# fmt: off
_FIRST_NAMES = (
    "Arjun", "Rohan", "Kabir", "Dev", "Ishaan", "Theo", "Callum", "Rhys", "Owen", "Felix",
    "Mateo", "Luca", "Joaquin", "Emre", "Kofi", "Tunde", "Yusuf", "Kenji", "Min-jun", "Lars",
    "Anders", "Pierre", "Bastien", "Nico", "Sami", "Idris", "Tomas", "Elias", "Jonah", "Malik",
)
_LAST_NAMES = (
    "Mehta", "Rao", "Sandhu", "Kapoor", "Ashworth", "Pellow", "Varga", "Okafor", "Mensah",
    "Ferreira", "Lindqvist", "Moreau", "Castellan", "Brannagh", "Tanaka", "Haddad", "Novak",
    "Delacroix", "Whitlock", "Oyelaran", "Strand", "Kowal", "Aldana", "Rourke", "Fennimore",
    "Quaye", "Holloway", "Marsh", "Ibarra", "Cutler",
)
# fmt: on


@dataclass(frozen=True)
class ClubSpec:
    id: str
    name: str
    short_name: str
    color: str
    strength: float
    star_name: str


CLUBS: tuple[ClubSpec, ...] = (
    ClubSpec("ashvale", "Ashvale Rovers", "ASH", "#B23A48", 1.15, "Theo Ashworth"),
    ClubSpec("kingsmere", "Kingsmere City", "KGC", "#2E5EAA", 1.12, "Rohan Mehta"),
    ClubSpec("northbrook", "Northbrook United", "NBU", "#C8102E", 1.05, "Kofi Mensah"),
    ClubSpec("riverford", "Riverford Athletic", "RIV", "#1F7A5C", 1.02, "Mateo Ferreira"),
    ClubSpec("stonegate", "Stonegate Albion", "STA", "#5B4B8A", 1.00, "Lars Lindqvist"),
    ClubSpec("westhaven", "Westhaven Town", "WHT", "#E0A526", 0.97, "Kenji Tanaka"),
    ClubSpec("calderbrook", "Calderbrook FC", "CAL", "#3A6B8C", 0.95, "Idris Haddad"),
    ClubSpec("elmhurst", "Elmhurst Wanderers", "ELM", "#2F4F2F", 0.92, "Callum Brannagh"),
    ClubSpec("harbourside", "Harbourside Rangers", "HBR", "#0E7C86", 0.90, "Arjun Sandhu"),
    ClubSpec("fenwick", "Fenwick Forest", "FEN", "#6B3E26", 0.88, "Nico Castellan"),
)


def build_team(spec: ClubSpec) -> Team:
    """Deterministic squad for a club: the same club always gets the same players."""
    rng = random.Random(spec.id)
    positions = [pos for pos, count in _FORMATION for _ in range(count)] + list(_BENCH)
    names = _unique_names(rng, len(positions), reserved=spec.star_name)
    # The star leads the line: first forward slot.
    star_index = positions.index(Position.FW)
    names[star_index] = spec.star_name

    numbers = rng.sample(range(2, 40), len(positions) - 1)
    players = tuple(
        Player(
            id=f"{spec.id}-{i:02d}",
            name=name,
            number=1 if i == 0 else numbers[i - 1],
            position=pos,
        )
        for i, (pos, name) in enumerate(zip(positions, names, strict=True))
    )
    return Team(
        id=spec.id,
        name=spec.name,
        short_name=spec.short_name,
        color=spec.color,
        strength=spec.strength,
        players=players,
        star_player_id=players[star_index].id,
    )


def _unique_names(rng: random.Random, count: int, reserved: str) -> list[str]:
    names: list[str] = []
    while len(names) < count:
        name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
        if name != reserved and name not in names:
            names.append(name)
    return names


TEAMS: dict[str, Team] = {spec.id: build_team(spec) for spec in CLUBS}

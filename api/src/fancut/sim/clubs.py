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
    ClubSpec("oakbridge", "Oakbridge Town", "OAK", "#7A1F2B", 1.18, "Pierre Delacroix"),
    ClubSpec("thornwick", "Thornwick United", "THW", "#1D3557", 1.08, "Dev Kapoor"),
    ClubSpec("copperhill", "Copperhill City", "CPH", "#B5651D", 1.06, "Yusuf Okafor"),
    ClubSpec("bramblefield", "Bramblefield FC", "BRM", "#4A6741", 1.03, "Emre Kowal"),
    ClubSpec("wyndmoor", "Wyndmoor Albion", "WYN", "#6D597A", 0.99, "Tunde Aldana"),
    ClubSpec("saltmarsh", "Saltmarsh Town", "SLT", "#457B9D", 0.96, "Sami Rourke"),
    ClubSpec("glenhallow", "Glenhallow Athletic", "GLH", "#2A9D8F", 0.93, "Bastien Quaye"),
    ClubSpec("hawkridge", "Hawkridge Wanderers", "HWK", "#9C2C2C", 0.91, "Jonah Ibarra"),
    ClubSpec("silverbeck", "Silverbeck Rovers", "SLV", "#8D99AE", 0.86, "Elias Strand"),
    ClubSpec("lindenpark", "Linden Park", "LDP", "#556B2F", 0.84, "Felix Novak"),
)


def build_team(spec: ClubSpec, taken: set[str]) -> Team:
    """Deterministic squad for a club. ``taken`` holds names already used league-wide,
    so no two players anywhere share a name."""
    rng = random.Random(spec.id)
    positions = [pos for pos, count in _FORMATION for _ in range(count)] + list(_BENCH)
    names = _unique_names(rng, len(positions), taken)
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


def _unique_names(rng: random.Random, count: int, taken: set[str]) -> list[str]:
    names: list[str] = []
    while len(names) < count:
        name = f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"
        if name not in taken:
            taken.add(name)
            names.append(name)
    return names


def _build_league_teams() -> dict[str, Team]:
    taken = {spec.star_name for spec in CLUBS}  # stars are reserved for their own clubs
    return {spec.id: build_team(spec, taken) for spec in CLUBS}


TEAMS: dict[str, Team] = _build_league_teams()

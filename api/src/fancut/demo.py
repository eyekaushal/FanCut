"""The demo's fans. Their names and clubs are fictional, like everything else."""

from fancut.profile import Depth, FanProfile, Language
from fancut.sim.clubs import TEAMS

_STARS = {team.id: team.star_player_id for team in TEAMS.values()}
_ARJUN_FANTASY_CLUBS = (
    "ashvale", "oakbridge", "northbrook", "riverford", "copperhill", "harbourside",
    "elmhurst", "saltmarsh", "glenhallow", "wyndmoor", "silverbeck",
)  # fmt: skip

ARJUN = FanProfile(
    name="Arjun",
    club_id="kingsmere",
    player_ids=(_STARS["kingsmere"], _STARS["thornwick"]),
    fantasy_squad=tuple(_STARS[club] for club in _ARJUN_FANTASY_CLUBS),
    captain_id=_STARS["ashvale"],
    language=Language.HINDI,
    depth=Depth.CASUAL,
)

MAYA = FanProfile(name="Maya", language=Language.ENGLISH, depth=Depth.ANALYST)

PROFILES = {profile.name.lower(): profile for profile in (ARJUN, MAYA)}

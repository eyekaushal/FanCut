import pytest

from fancut.matchday.matchday import Matchday, build_matchday
from fancut.sim import Match, build_league


@pytest.fixture(scope="session")
def league() -> list[Match]:
    """The default 30-match league, built once per test session."""
    return build_league(2026)


@pytest.fixture(scope="session")
def matchday() -> Matchday:
    """The demo matchday: ten simultaneous matches, built once per test session."""
    return build_matchday(34)

import pytest

from fancut.sim import Match, build_league


@pytest.fixture(scope="session")
def league() -> list[Match]:
    """The default 30-match league, built once per test session."""
    return build_league(2026)

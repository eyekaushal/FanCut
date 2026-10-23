import pytest
from pydantic import ValidationError

from fancut.profile import FanProfile


def test_captain_must_be_in_the_fantasy_squad() -> None:
    with pytest.raises(ValidationError, match="captain"):
        FanProfile(name="x", fantasy_squad=("a", "b"), captain_id="c")


def test_fantasy_squad_is_limited_to_fifteen() -> None:
    with pytest.raises(ValidationError):
        FanProfile(name="x", fantasy_squad=tuple(str(i) for i in range(16)))


def test_followed_and_fantasy_players_both_count() -> None:
    fan = FanProfile(name="x", player_ids=("p1",), fantasy_squad=("p2",))
    assert fan.cares_about_player("p1") and fan.cares_about_player("p2")
    assert not fan.cares_about_player("p3")

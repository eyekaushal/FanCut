import pytest

from fancut.drama.measures import surprise, suspense, total_variation
from fancut.drama.probability import Outcome

RATE = 0.016


def test_no_suspense_once_the_match_is_over() -> None:
    assert suspense(1, 1, RATE, RATE, 0) == 0.0


def test_a_tight_late_game_is_more_suspenseful_than_a_settled_one() -> None:
    assert suspense(1, 1, RATE, RATE, 8) > suspense(4, 0, RATE, RATE, 8)


def test_suspense_grows_as_a_tied_game_runs_out_of_time() -> None:
    assert suspense(0, 0, RATE, RATE, 10) > suspense(0, 0, RATE, RATE, 85)


def test_more_attacking_threat_means_more_suspense() -> None:
    assert suspense(1, 1, 3 * RATE, 3 * RATE, 10) > suspense(1, 1, RATE, RATE, 10)


def test_surprise_and_total_variation() -> None:
    before = Outcome(0.5, 0.3, 0.2)
    after = Outcome(0.8, 0.15, 0.05)
    assert surprise(before, before) == 0.0
    assert surprise(before, after) == pytest.approx(surprise(after, before))
    assert total_variation(before, after) == pytest.approx(0.3)
    assert total_variation(Outcome(1, 0, 0), Outcome(0, 0, 1)) == pytest.approx(1.0)

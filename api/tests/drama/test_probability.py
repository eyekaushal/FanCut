import pytest

from fancut.drama.probability import outcome_probabilities, pre_match_rates


def test_probabilities_form_a_distribution() -> None:
    for score, left in [((0, 0), 94), ((2, 1), 30), ((0, 3), 5), ((1, 1), 0.5)]:
        p = outcome_probabilities(*score, 0.016, 0.014, left)
        assert sum(p) == pytest.approx(1.0)
        assert all(0.0 <= x <= 1.0 for x in p)


def test_pre_match_odds_for_equal_teams_look_like_real_football() -> None:
    home, draw, away = outcome_probabilities(0, 0, *pre_match_rates(1.0, 1.0), 94)
    assert 0.38 <= home <= 0.48
    assert 0.22 <= draw <= 0.30
    assert away < home


def test_stronger_side_is_favoured() -> None:
    strong_home = outcome_probabilities(0, 0, *pre_match_rates(1.15, 0.88), 94)
    weak_home = outcome_probabilities(0, 0, *pre_match_rates(0.88, 1.15), 94)
    assert strong_home.home > weak_home.home


def test_no_time_left_means_the_result_is_certain() -> None:
    assert outcome_probabilities(2, 1, 0.02, 0.02, 0) == (1.0, 0.0, 0.0)
    assert outcome_probabilities(1, 1, 0.02, 0.02, 0) == (0.0, 1.0, 0.0)


def test_a_lead_is_safer_the_less_time_remains() -> None:
    leads = [outcome_probabilities(1, 0, 0.016, 0.016, left).home for left in (60, 30, 10, 1)]
    assert leads == sorted(leads)
    assert leads[-1] > 0.95

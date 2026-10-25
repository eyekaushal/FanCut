import json
from pathlib import Path

from fancut.evals.director import markdown, measure_director
from fancut.evals.results import load_results, save_result
from fancut.matchday.matchday import Matchday


def test_the_director_measurement_reuses_a_known_matchday_and_pools(matchday: Matchday) -> None:
    seen: list[int] = []
    result = measure_director([34], known=matchday, on_progress=seen.append)
    assert seen == [1]
    assert result.seeds == [34] and result.fans == ["Arjun", "Maya"]
    assert result.personal_coverage == 1.0 and result.early_cuts == 0
    assert result.decisive_goals > 0 and 0 < result.live_coverage <= 1
    assert result.distinctness_min == result.distinctness_max >= 0.5
    assert len(result.per_matchday) == 2
    table = markdown(result)
    assert "| Personal coverage |" in table and "seeds 34" in table


def test_results_load_what_exists_and_ignore_the_rest(tmp_path: Path) -> None:
    assert load_results(tmp_path) == {"director": None, "redteam": None, "foundry": None}
    path = save_result("director", {"seeds": [34]}, tmp_path)
    assert json.loads(path.read_text()) == {"seeds": [34]}
    (tmp_path / "foundry.json").write_text("not json")
    found = load_results(tmp_path)
    assert found["director"] == {"seeds": [34]} and found["foundry"] is None

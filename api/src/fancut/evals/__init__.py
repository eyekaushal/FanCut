"""Evaluations: the Director measured over matchdays, the Fact Checker red-teamed, and
the Narrator scored by Foundry's evaluators.

    uv run python -m fancut.evals director    # no Azure needed; deterministic
    uv run python -m fancut.evals redteam     # rules locally; the judge with a model
    uv run python -m fancut.evals foundry     # needs a model and `uv sync --group evals`

Each command writes its results next to this package (``results/``), where the API
serves them on ``/evaluation`` and the Studio shows them.
"""

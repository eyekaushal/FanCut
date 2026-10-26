# FanCut API

Python 3.12 package `fancut`: the synthetic league (`sim`), the Drama Engine (`drama`), the
Director (`director`), the agents (`agents`), per-player numbers (`insights`), the HTTP, SSE
and MCP layer (`api`) and the evaluations (`evals`). See [`docs/architecture.md`](../docs/architecture.md).

```bash
uv sync                  # install
cp .env.example .env     # configure (empty keys are fine: templates speak, no voice)
uv run fancut            # serve on http://127.0.0.1:8000  (GET /health, docs at /docs)
uv run pytest            # tests
uv run ruff check . && uv run ruff format --check . && uv run mypy   # quality gates

uv run python -m fancut.director            # two fans' channels on one matchday, printed
uv run python -m fancut.agents narrate --fan arjun --language hi   # narration from a terminal
uv run python -m fancut.evals director      # measure the Director; see ../evals/README.md
uv run python -m fancut.check               # verify the Foundry model and Speech keys
```

Configuration is read from environment variables with the prefix `NK_` or from `api/.env`
(see `.env.example`). `api/.env` is git-ignored and must never be committed.

# Nightkeeper API

Python 3.12 service: synthetic league, drama engine, wake decisions, agents.

```bash
uv sync                  # install
cp .env.example .env     # configure
uv run nightkeeper       # serve on http://127.0.0.1:8000  (GET /health)
uv run pytest            # tests
uv run ruff check . && uv run ruff format --check . && uv run mypy   # quality gates
```

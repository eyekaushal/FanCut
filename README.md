# FanCut

**Watches the match while you sleep. Wakes you before the moment that matters.**

The biggest Premier League games kick off after midnight for hundreds of millions of fans. FanCut watches a live match on your behalf. It wakes you when the game is *about to* become decisive (rising suspense, not a goal that already happened), and the next morning gives you a spoiler-free verdict and a replay plan that fits the time you have. English, हिंदी and Hinglish.

> Built for **Inside the Game: Developer Hackathon** (Microsoft x Premier League) on synthetic, football-realistic data. No real match data, footage or marks are used.

## Repository layout

| Path | What lives there |
|---|---|
| [`api/`](api/) | Python 3.12 service: synthetic league, drama engine, wake decisions, agents |
| [`web/`](web/) | Next.js web app (PWA) |
| [`evals/`](evals/) | Evaluation datasets and evaluator configs |
| [`infra/`](infra/) | Azure infrastructure as code |
| [`docs/`](docs/) | Architecture notes and decision records |

## Quick start

```bash
# API
cd api && uv sync && cp .env.example .env && uv run fancut   # http://127.0.0.1:8000/health

# Web
cd web && npm ci && npm run dev                                  # http://localhost:3000
```

## License

[MIT](LICENSE)

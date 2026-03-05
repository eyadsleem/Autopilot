# SnapTrader-style Decision Support Platform

This repository now includes a backend + frontend starter for a SnapTrader-like workflow:

- **Market ingestion + indicator extraction** (OHLCV, RSI, MACD, ATR)
- **Multimodal chart analysis** (OpenAI/Anthropic integration with heuristic fallback)
- **Signal and risk engine** (trade plan + position sizing)
- **SnapTrade integration endpoints** (account linking + portfolio sync)
- **Alerting service** (pattern watchlist with webhook/email/slack channels)
- **Next.js frontend shell with auth**

## Backend quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend docs: `http://127.0.0.1:8000/docs`

### Backend endpoints

Public:
- `GET /health`
- `POST /auth/login`
- `GET /market/{symbol}?interval=1d&period=3mo`
- `POST /analyze-chart`
- `POST /trade-plan`

Protected (Bearer token from `/auth/login`):
- `GET /snaptrade/connect/{user_id}`
- `GET /snaptrade/portfolio/{user_id}`
- `POST /alerts`
- `GET /alerts`
- `POST /alerts/trigger`

## Environment variables

- `DEMO_AUTH_TOKEN` (default: `dev-token`)
- `VISION_PROVIDER` (`heuristic` | `openai` | `anthropic`)
- `OPENAI_API_KEY`, `OPENAI_VISION_MODEL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_VISION_MODEL`
- `SNAPTRADE_BASE_URL`, `SNAPTRADE_CLIENT_ID`, `SNAPTRADE_CONSUMER_KEY`

## Frontend quickstart

```bash
cd frontend
npm install
npm run dev
```

Open UI: `http://localhost:3000`

## Notes

- If no vision API key is configured, chart analysis automatically falls back to heuristic mode.
- SnapTrade service has a safe local fallback payload when API credentials are unavailable.
- Email/Slack dispatch is intentionally mocked in MVP mode; webhook delivery is real HTTP POST.

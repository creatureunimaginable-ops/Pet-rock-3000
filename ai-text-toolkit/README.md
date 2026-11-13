# AI Text Toolkit

A free-tier-friendly web app for AI text tools: **Summarize**, **Rewrite** (4 tones), and **Captions** (Instagram / Twitter / LinkedIn). Built with FastAPI + vanilla JS, SQLite storage, and a daily free-credit system for the freemium model.

## Features

- 3 AI text tools with per-tool options
- Daily free credits per user (client-based, no signup), configurable
- Generation history per user (last 20)
- Pluggable AI providers: **Mistral**, **OpenAI**, or **mock/demo mode** (no key needed)
- Single-page UI, no build step

## Quick start (one click)

**Windows:** double-click `start.bat`

**Mac / Linux:**
```bash
bash start.sh
```

The script installs everything on first run, starts the app, and opens your browser at http://127.0.0.1:8000. The app starts in **demo mode** so you can try everything without an API key.

> Requires Python 3.10+ ([python.org](https://www.python.org/downloads/) — on Windows, check "Add Python to PATH" during install).

## Enable a real AI provider

Set your provider and key, then start the app:

```bash
export AI_PROVIDER=mistral
export AI_API_KEY=your-key-here
bash start.sh
```

- Mistral free key: https://console.mistral.ai
- OpenAI: https://platform.openai.com

## Configuration

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `mock` | `mock`, `mistral`, or `openai` |
| `AI_API_KEY` | — | Provider API key (required for real providers) |
| `AI_MODEL` | provider default | e.g. `mistral-small-latest`, `gpt-4o-mini` |
| `FREE_DAILY_CREDITS` | `5` | Free uses per user per day |
| `PORT` | `8000` | Server port |
| `DATABASE_PATH` | `toolkit.db` | SQLite file path |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/tools` | Tool list + app config |
| GET | `/api/credits/{client_id}` | Remaining credits today |
| POST | `/api/tools/{tool}` | Run a tool (`client_id`, `text`, `options`) |
| GET | `/api/history/{client_id}` | Last 20 generations |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Monetization path (freemium)

- Free: N credits/day (set via `FREE_DAILY_CREDITS`)
- Paid ideas: raise the limit behind Stripe checkout, add watermark-free / longer outputs, team accounts

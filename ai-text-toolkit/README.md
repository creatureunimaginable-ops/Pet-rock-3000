> Requires Python 3.10+ ([python.org](https://www.python.org/downloads/) — on Windows, check "Add Python to PATH" during install).

## Put it online (free — use it from your phone)

The repo includes a `Dockerfile` and a Render blueprint (`render.yaml`), so it deploys in a few taps:

1. Merge this pull request (or deploy straight from this branch)
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect your GitHub account and pick this repository
4. Click **Apply** — Render builds and gives you a public `https://your-app.onrender.com` URL

Notes:
- Free tier: the app sleeps after 15 min idle and wakes on the first request (~30s)
- SQLite storage resets on redeploy; add a Render disk or Postgres for persistence
- To enable real AI: add `AI_PROVIDER` / `AI_API_KEY` environment variables in the Render dashboard

## Enable a real AI provider
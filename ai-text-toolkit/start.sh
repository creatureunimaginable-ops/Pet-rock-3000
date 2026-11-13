#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Install it from https://www.python.org/downloads/ and run this again."
  exit 1
fi
if [ ! -d .venv ]; then
  echo "First run: setting things up, this takes a minute..."
  python3 -m venv .venv
  ./.venv/bin/pip install -q -r requirements.txt
fi
echo ""
echo "============================================"
echo "  AI Text Toolkit starting..."
echo "  Open http://127.0.0.1:8000 in your browser"
echo "  Press Ctrl+C to stop the app."
echo "============================================"
echo ""
( sleep 3; xdg-open http://127.0.0.1:8000 >/dev/null 2>&1 || open http://127.0.0.1:8000 >/dev/null 2>&1 || true ) &
exec ./.venv/bin/python run.py

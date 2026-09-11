#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PORT_API="8000"
PORT_STREAMLIT="8501"

# Clean stale processes on the app ports so a single run command is reliable.
if command -v lsof >/dev/null 2>&1; then
  echo "Cleaning up previous app processes on ports $PORT_API and $PORT_STREAMLIT..."
  lsof -ti tcp:"$PORT_API" | xargs -r kill -9 || true
  lsof -ti tcp:"$PORT_STREAMLIT" | xargs -r kill -9 || true
fi

python -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT_API" &
API_PID=$!

python -m streamlit run ui/streamlit_app.py --server.headless true --server.port "$PORT_STREAMLIT"
STREAMLIT_EXIT=$?

kill "$API_PID" || true
wait "$API_PID" 2>/dev/null || true

exit "$STREAMLIT_EXIT"

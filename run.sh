#!/usr/bin/env bash
# Starts both the FastAPI backend and the Next.js frontend in the background,
# waits until both respond, opens the app in the default browser, then tails
# both logs. Press Ctrl+C to stop watching (servers keep running in background).
#
# Usage:  ./run.sh   (from Git Bash / WSL / any POSIX shell)

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_LOG="$ROOT/backend/.run-backend.log"
FRONTEND_LOG="$ROOT/frontend/.run-frontend.log"

echo "Starting backend (FastAPI) on http://localhost:8000 ..."
(
  cd "$ROOT/backend"
  ./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
) > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "Starting frontend (Next.js) on http://localhost:3000 ..."
(
  cd "$ROOT/frontend"
  NEXT_PUBLIC_API_URL=http://localhost:8000 npx next dev --port 3000
) > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo "Waiting for both servers to come up..."
backend_up=false
frontend_up=false
for i in $(seq 1 40); do
  if [ "$backend_up" = false ] && curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null | grep -q 200; then
    backend_up=true
  fi
  if [ "$frontend_up" = false ] && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null | grep -q 200; then
    frontend_up=true
  fi
  if [ "$backend_up" = true ] && [ "$frontend_up" = true ]; then break; fi
  sleep 1.5
done

if [ "$backend_up" = true ] && [ "$frontend_up" = true ]; then
  echo "Both servers are up!"
  echo "  Backend:  http://localhost:8000  (docs at /docs)   [pid $BACKEND_PID, log: $BACKEND_LOG]"
  echo "  Frontend: http://localhost:3000                    [pid $FRONTEND_PID, log: $FRONTEND_LOG]"
  (cmd.exe /c start http://localhost:3000) 2>/dev/null || true
else
  echo "Timed out waiting for servers. Check the logs:"
  echo "  $BACKEND_LOG"
  echo "  $FRONTEND_LOG"
fi

echo ""
echo "Servers are running in the background (pids $BACKEND_PID, $FRONTEND_PID)."
echo "To stop them:  kill $BACKEND_PID $FRONTEND_PID"

#!/bin/sh
set -e
cd /app/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null || true' INT TERM EXIT
nginx -g 'daemon off;'

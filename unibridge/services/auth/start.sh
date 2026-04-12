#!/bin/sh
# start.sh — Auth Service entrypoint
# Runs seed.py first (idempotent: skips if users already exist), then starts uvicorn.

set -e

echo "[auth] Running database seed..."
python seed.py

echo "[auth] Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8001

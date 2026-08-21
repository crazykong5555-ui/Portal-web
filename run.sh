#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/Scripts/python.exe" ]; then
  if command -v py >/dev/null 2>&1; then
    py -3.13 -m venv .venv
  else
    python -m venv .venv
  fi
fi

.venv/Scripts/python.exe -m pip install -r requirements.txt

export MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
export MYSQL_USER="${MYSQL_USER:-root}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-BaseDeDatos555}"
export MYSQL_DB="${MYSQL_DB:-portal}"
export MYSQL_PORT="${MYSQL_PORT:-3306}"

.venv/Scripts/python.exe App.py

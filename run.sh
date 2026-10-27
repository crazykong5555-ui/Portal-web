#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt

# Local-only defaults. Production settings belong in the hosting provider's secrets.
export APP_ENV="${APP_ENV:-development}"
export MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
export MYSQL_USER="${MYSQL_USER:-root}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
export MYSQL_DB="${MYSQL_DB:-portal}"
export MYSQL_PORT="${MYSQL_PORT:-3306}"
export MYSQL_SSL="${MYSQL_SSL:-disabled}"

.venv/bin/python App.py

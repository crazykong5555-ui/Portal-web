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

export MYSQLHOST="${MYSQLHOST:-localhost}"
export MYSQLUSER="${MYSQLUSER:-root}"
export MYSQLPASSWORD="${MYSQLPASSWORD:-BaseDeDatos555}"
export MYSQLDATABASE="${MYSQLDATABASE:-portal}"
export MYSQLPORT="${MYSQLPORT:-3306}"

.venv/Scripts/python.exe App.py

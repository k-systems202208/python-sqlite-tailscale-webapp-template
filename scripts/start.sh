#!/usr/bin/env sh
set -eu
if [ ! -x .venv/bin/python ]; then
  echo "Virtual environment not found. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi
exec .venv/bin/python run.py

#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")
PYTHON="$REPO_ROOT/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "Virtual environment not found. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

cd "$REPO_ROOT"
"$PYTHON" -m scripts.doctor
"$PYTHON" -m pip check
"$PYTHON" -m ruff check .
"$PYTHON" -m ruff format --check .
"$PYTHON" -m pytest --cov=app --cov=scripts --cov-report=term-missing --cov-fail-under=80

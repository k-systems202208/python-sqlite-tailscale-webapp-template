#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.11-3.14 was not found in PATH." >&2
  exit 1
fi

if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info < (3, 15) else 1)'; then
  echo "Python 3.11-3.14 is required." >&2
  exit 1
fi

cd "$REPO_ROOT"
"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

echo "Development bootstrap complete."
echo "Next: cp .env.example .env"
echo "Then: ./scripts/check.sh"
echo "Then: ./scripts/start.sh"

#!/usr/bin/env sh
set -eu
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

echo "Bootstrap complete."
echo "Next: cp .env.example .env"
echo "Then: ./scripts/start.sh"

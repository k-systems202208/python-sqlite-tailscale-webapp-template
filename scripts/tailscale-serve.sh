#!/usr/bin/env sh
set -eu
PORT="${1:-8000}"
tailscale serve --bg "$PORT"
tailscale serve status

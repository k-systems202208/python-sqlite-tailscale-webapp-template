param([int]$Port = 8000)
$ErrorActionPreference = "Stop"

tailscale serve --bg $Port
tailscale serve status

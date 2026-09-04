$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ was not found in PATH."
}

& python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.11 or newer is required."
}

Push-Location $repoRoot
try {
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip
    & .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
}
finally {
    Pop-Location
}

Write-Host "Development bootstrap complete."
Write-Host "Next: Copy-Item .env.example .env"
Write-Host "Then: .\scripts\check.ps1"
Write-Host "Then: .\scripts\start.ps1"

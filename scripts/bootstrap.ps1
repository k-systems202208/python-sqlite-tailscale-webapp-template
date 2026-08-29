$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ was not found in PATH."
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

Write-Host "Bootstrap complete."
Write-Host "Next: Copy-Item .env.example .env"
Write-Host "Then: .\\scripts\\start.ps1"

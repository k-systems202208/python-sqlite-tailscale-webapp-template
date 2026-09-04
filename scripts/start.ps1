$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Virtual environment not found. Run .\scripts\bootstrap.ps1 first."
}

Push-Location $repoRoot
try {
    & $python run.py
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

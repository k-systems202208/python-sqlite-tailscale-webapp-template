$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Virtual environment not found. Run .\scripts\bootstrap.ps1 first."
}

Push-Location $repoRoot
try {
    & $python -m scripts.doctor
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m pip check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m ruff format --check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $python -m pytest --cov=app --cov=scripts.db_tools --cov-report=term-missing --cov-fail-under=80
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}

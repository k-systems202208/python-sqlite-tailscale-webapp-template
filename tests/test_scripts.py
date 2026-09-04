from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_scripts_require_python_311_or_newer():
    for relative_path in [
        "scripts/bootstrap.ps1",
        "scripts/bootstrap.sh",
        "scripts/bootstrap-runtime.ps1",
        "scripts/bootstrap-runtime.sh",
    ]:
        script = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "3.11" in script
        assert "sys.version_info >= (3, 11)" in script


def test_dependency_files_use_constraints():
    assert "-c constraints.txt" in (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "-c constraints.txt" in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")


def test_quality_scripts_run_lint_format_and_coverage():
    for relative_path in ["scripts/check.ps1", "scripts/check.sh"]:
        script = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "ruff check" in script
        assert "ruff format --check" in script
        assert "--cov-fail-under=80" in script

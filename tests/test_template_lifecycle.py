from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_doctor_is_part_of_local_and_ci_quality_flow():
    assert (ROOT / "scripts" / "doctor.py").is_file()
    assert "-m scripts.doctor" in read("scripts/check.ps1")
    assert "-m scripts.doctor" in read("scripts/check.sh")
    assert "python -m scripts.doctor" in read(".github/workflows/ci.yml")


def test_operations_runbook_uses_existing_health_and_recovery_tools():
    operations = read("docs/OPERATIONS.md")

    assert "/healthz" in operations
    assert "/readyz" in operations
    assert "scripts.db_tools" in operations
    assert "Restore" in operations
    assert "Tailscale" in operations


def test_extension_guide_keeps_domain_features_outside_common_core():
    extending = read("docs/EXTENDING.md")

    assert "app/features/equipment/" in extending
    assert "register(app)" in extending
    assert "Service" in extending
    assert "Migration" in extending
    assert "SQLでも認可" in extending


def test_readme_links_doctor_operations_and_extension_guidance():
    readme = read("README.md")

    assert "python -m scripts.doctor" in readme
    assert "docs/OPERATIONS.md" in readme
    assert "docs/EXTENDING.md" in readme

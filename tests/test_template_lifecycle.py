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


def test_beginner_guide_explains_the_full_github_desktop_workflow():
    beginner = read("BEGINNER-GUIDE.md")

    assert "GitHub Desktop" in beginner
    assert "Commit" in beginner
    assert "Push" in beginner
    assert "Pull Request" in beginner
    assert "CI" in beginner
    assert "Squash Merge" in beginner
    assert "Conflict" in beginner
    assert "ChatGPT / Codex" in beginner


def test_sampleless_smoke_test_protects_the_reusable_common_core():
    ci = read(".github/workflows/ci.yml")
    smoke_test = read("docs/TEMPLATE-SMOKE-TEST.md")

    assert "Sampleless template smoke test" in ci
    assert "rm -rf app/features/items" in ci
    assert "--cov-fail-under=80" in ci
    assert "Use this template" in smoke_test
    assert "app/features/items/" in smoke_test
    assert "scripts/check" in smoke_test
    assert "Pull Request" in smoke_test


def test_manual_smoke_test_keeps_real_world_third_party_findings():
    smoke_test = read("docs/TEMPLATE-SMOKE-TEST.md")

    assert "Rulesetは引き継がれません" in smoke_test
    assert "GitHub連携のアクセス対象" in smoke_test
    assert "別テンプレートの `setup-github.ps1`" in smoke_test
    assert "次の未使用version" in smoke_test
    assert "docs/OPERATIONS.md" in smoke_test
    assert "docs/EXTENDING.md" in smoke_test
    assert "merge後main CI" in smoke_test


def test_main_guides_link_beginner_guidance_and_lifecycle_docs():
    readme = read("README.md")
    getting_started = read("GETTING-STARTED.md")
    development = read("docs/DEVELOPMENT.md")
    github_setup = read("docs/GITHUB-SETUP.md")

    assert "BEGINNER-GUIDE.md" in readme
    assert "BEGINNER-GUIDE.md" in getting_started
    assert "BEGINNER-GUIDE.md" in development
    assert "BEGINNER-GUIDE.md" in github_setup
    assert "python -m scripts.doctor" in readme
    assert "docs/OPERATIONS.md" in readme
    assert "docs/EXTENDING.md" in readme
    assert "docs/TEMPLATE-SMOKE-TEST.md" in readme
    assert "TEMPLATE-SMOKE-TEST.md" in development

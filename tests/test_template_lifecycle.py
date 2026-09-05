import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def markdown_files() -> list[Path]:
    files = list(ROOT.glob("*.md"))
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / ".github").rglob("*.md"))
    return sorted(set(files))


def test_doctor_is_part_of_local_and_ci_quality_flow():
    assert (ROOT / "scripts" / "doctor.py").is_file()
    assert "-m scripts.doctor" in read("scripts/check.ps1")
    assert "-m scripts.doctor" in read("scripts/check.sh")
    assert "python -m scripts.doctor" in read(".github/workflows/ci.yml")


def test_supported_python_range_matches_ci_matrix():
    pyproject = read("pyproject.toml")
    doctor = read("scripts/doctor.py")
    ci = read(".github/workflows/ci.yml")
    getting_started = read("GETTING-STARTED.md")
    bootstrap_scripts = [
        read("scripts/bootstrap.ps1"),
        read("scripts/bootstrap.sh"),
        read("scripts/bootstrap-runtime.ps1"),
        read("scripts/bootstrap-runtime.sh"),
    ]

    assert 'requires-python = ">=3.11,<3.15"' in pyproject
    assert "SUPPORTED_PYTHON_MIN = (3, 11)" in doctor
    assert "SUPPORTED_PYTHON_MAX_EXCLUSIVE = (3, 15)" in doctor
    assert 'python-version: ["3.11", "3.12", "3.13", "3.14"]' in ci
    assert "Python 3.11〜3.14" in getting_started
    for script in bootstrap_scripts:
        assert "(3, 11) <= sys.version_info < (3, 15)" in script
        assert "3.11-3.14" in script


def test_coverage_targets_match_configuration_and_local_ci_commands():
    pyproject = read("pyproject.toml")
    ci = read(".github/workflows/ci.yml")
    check_ps1 = read("scripts/check.ps1")
    check_sh = read("scripts/check.sh")
    development = read("docs/DEVELOPMENT.md")

    assert 'source = ["app", "scripts"]' in pyproject
    assert "--cov=app" in ci
    assert "--cov=scripts" in ci
    assert "--cov=scripts.db_tools" not in ci
    assert "--cov=scripts" in check_ps1
    assert "--cov=scripts" in check_sh
    assert "`app` とPython utilityを含む `scripts` 全体" in development


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


def test_verification_design_is_part_of_issue_pr_and_contribution_contract():
    quality = read("docs/QUALITY-VERIFICATION.md")
    issue_template = read(".github/ISSUE_TEMPLATE/change-request.md")
    pr_template = read(".github/pull_request_template.md")
    contributing = read("CONTRIBUTING.md")

    for content in [quality, issue_template, pr_template, contributing]:
        assert "Verification Plan" in content
        assert "Risk Level" in content
        assert "Test Oracle" in content
        assert "Independent Verification" in content

    assert "Falsification" in quality
    assert "Greenだけでは保証しない範囲" in pr_template
    assert "High Risk" in quality
    assert "Coverage 100%" in quality
    assert "Mutation Testing" in quality
    assert "QUALITY-VERIFICATION.md" in contributing


def test_github_actions_are_pinned_and_ruleset_requires_up_to_date_branch():
    ci = read(".github/workflows/ci.yml")
    action_refs = re.findall(r"uses:\s+([^\s#]+)", ci)

    assert action_refs
    for action_ref in action_refs:
        if action_ref.startswith("./"):
            continue
        assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", action_ref), action_ref

    ruleset = json.loads(read("github/protect-main.ruleset.json"))
    status_rule = next(rule for rule in ruleset["rules"] if rule["type"] == "required_status_checks")
    assert status_rule["parameters"]["strict_required_status_checks_policy"] is True


def test_security_policy_is_separate_from_security_design():
    policy = read(".github/SECURITY.md")
    design = read("docs/SECURITY.md")

    assert "Reporting a vulnerability" in policy
    assert "Public Issue" in policy
    assert "docs/SECURITY.md" in policy
    assert "セキュリティ境界" in design


def test_repository_internal_markdown_links_resolve():
    root = ROOT.resolve()
    broken: list[str] = []

    for source in markdown_files():
        content = source.read_text(encoding="utf-8")
        for raw_target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
            target = raw_target.strip()
            if target.startswith("<") and ">" in target:
                target = target[1 : target.index(">")]
            else:
                target = target.split(maxsplit=1)[0]

            if not target or target.startswith(("#", "/", "http://", "https://", "mailto:", "tel:")):
                continue

            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue

            candidate = (source.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                broken.append(f"{source.relative_to(ROOT)} -> {raw_target} (outside repository)")
                continue

            if not candidate.exists():
                broken.append(f"{source.relative_to(ROOT)} -> {raw_target}")

    assert not broken, "Broken internal Markdown links:\n" + "\n".join(broken)


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

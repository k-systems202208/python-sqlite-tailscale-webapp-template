import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_protect_main_ruleset_matches_template_policy():
    ruleset_path = ROOT / "github" / "protect-main.ruleset.json"
    ruleset = json.loads(ruleset_path.read_text(encoding="utf-8"))

    assert ruleset["name"] == "Protect main"
    assert ruleset["target"] == "branch"
    assert ruleset["enforcement"] == "active"
    assert ruleset["bypass_actors"] == []
    assert ruleset["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]

    rules = {rule["type"]: rule for rule in ruleset["rules"]}
    assert {"deletion", "non_fast_forward", "required_linear_history"} <= set(rules)

    pull_request = rules["pull_request"]["parameters"]
    assert pull_request["required_approving_review_count"] == 0
    assert pull_request["required_review_thread_resolution"] is True
    assert pull_request["allowed_merge_methods"] == ["squash"]

    checks = rules["required_status_checks"]["parameters"]
    assert checks["strict_required_status_checks_policy"] is True
    assert checks["do_not_enforce_on_create"] is False
    assert {check["context"] for check in checks["required_status_checks"]} == {
        "test (3.11)",
        "test (3.12)",
        "test (3.13)",
        "test (3.14)",
        "windows-powershell-51",
    }


def test_setup_script_applies_repository_policy():
    script = (ROOT / "scripts" / "setup-github.ps1").read_text(encoding="utf-8")

    required_fragments = [
        "allow_squash_merge=true",
        "allow_merge_commit=false",
        "allow_rebase_merge=false",
        "delete_branch_on_merge=true",
        "allow_update_branch=true",
        "protect-main.ruleset.json",
        "repos/$Repository/rulesets",
    ]

    for fragment in required_fragments:
        assert fragment in script


def test_template_repository_setup_is_scoped_and_verifies_live_settings():
    path = ROOT / "scripts" / "setup-template-repository.ps1"
    assert path.is_file()

    script = path.read_text(encoding="utf-8")
    required_fragments = [
        "setup-github.ps1",
        "permissions.admin",
        "is_template",
        "has_wiki=false",
        "repos/$Repository/topics",
        "strict_required_status_checks_policy",
        '"python"',
        '"flask"',
        '"sqlite"',
        '"tailscale"',
        '"webapp-template"',
        '"starter-template"',
    ]

    for fragment in required_fragments:
        assert fragment in script

    assert "派生アプリのWiki / Topicsは自動変更しません" in script


def test_template_repository_setup_avoids_full_json_parsing_on_powershell_51():
    script = (ROOT / "scripts" / "setup-template-repository.ps1").read_text(encoding="utf-8")

    assert "ConvertFrom-Json" not in script
    for jq_expression in [
        '"--jq", ".permissions.admin"',
        '"--jq", ".is_template"',
        '"--jq", ".has_wiki"',
        '"--jq", ".names[]"',
        "strict_required_status_checks_policy",
    ]:
        assert jq_expression in script

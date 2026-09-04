from pathlib import Path

from scripts.doctor import diagnose, parse_env

REQUIRED_FILES = (
    "pyproject.toml",
    "requirements.txt",
    "constraints.txt",
    ".env.example",
)


def make_repo(tmp_path: Path) -> Path:
    for name in REQUIRED_FILES:
        (tmp_path / name).write_text("test\n", encoding="utf-8")
    return tmp_path


def test_parse_env_ignores_comments_and_reads_values():
    assert parse_env("# comment\nA=1\nB = 'two'\n") == {"A": "1", "B": "two"}


def test_doctor_allows_missing_optional_setup(tmp_path):
    root = make_repo(tmp_path)

    result = diagnose(root=root, version_info=(3, 11, 9), which=lambda _command: None)

    assert result["failed"] is False
    messages = [check["message"] for check in result["checks"]]
    assert any(".venv は未作成" in message for message in messages)
    assert any(".env は未作成" in message for message in messages)
    assert any("APP_DATA_DIR は未作成" in message for message in messages)


def test_doctor_reads_env_and_existing_data_dir(tmp_path):
    root = make_repo(tmp_path)
    data_dir = root / "runtime-data"
    data_dir.mkdir()
    (root / ".env").write_text("APP_DATA_DIR=runtime-data\n", encoding="utf-8")

    result = diagnose(
        root=root,
        version_info=(3, 14, 1),
        which=lambda command: f"/usr/bin/{command}",
    )

    assert result["failed"] is False
    assert any(
        check["level"] == "PASS" and "APP_DATA_DIR を確認" in check["message"]
        for check in result["checks"]
    )
    assert all(
        check["level"] == "PASS"
        for check in result["checks"]
        if "command:" in check["message"]
    )


def test_doctor_fails_unsupported_python(tmp_path):
    root = make_repo(tmp_path)

    result = diagnose(root=root, version_info=(3, 10, 14), which=lambda _command: None)

    assert result["failed"] is True
    assert any(
        check["level"] == "FAIL" and "Python 3.10.14 は対象外" in check["message"]
        for check in result["checks"]
    )


def test_doctor_fails_missing_required_file(tmp_path):
    root = make_repo(tmp_path)
    (root / "constraints.txt").unlink()

    result = diagnose(root=root, version_info=(3, 11, 0), which=lambda _command: None)

    assert result["failed"] is True
    assert any(
        check["level"] == "FAIL" and "constraints.txt がありません" in check["message"]
        for check in result["checks"]
    )


def test_doctor_fails_when_data_path_is_a_file(tmp_path):
    root = make_repo(tmp_path)
    (root / ".env").write_text("APP_DATA_DIR=not-a-directory\n", encoding="utf-8")
    (root / "not-a-directory").write_text("file\n", encoding="utf-8")

    result = diagnose(root=root, version_info=(3, 11, 0), which=lambda _command: None)

    assert result["failed"] is True
    assert any(
        check["level"] == "FAIL" and "directoryではありません" in check["message"]
        for check in result["checks"]
    )

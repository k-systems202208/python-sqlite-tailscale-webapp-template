from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = (
    "pyproject.toml",
    "requirements.txt",
    "constraints.txt",
    ".env.example",
)
OPTIONAL_TOOLS = ("git", "gh", "tailscale")
SUPPORTED_PYTHON_MIN = (3, 11)
SUPPORTED_PYTHON_MAX_EXCLUSIVE = (3, 15)


def parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name:
            values[name] = value.strip().strip('"').strip("'")
    return values


def _venv_exists(root: Path) -> bool:
    if os.name == "nt":
        return (root / ".venv" / "Scripts" / "python.exe").is_file()
    return (root / ".venv" / "bin" / "python").is_file()


def diagnose(
    *,
    root: Path = ROOT,
    version_info: tuple[int, ...] | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> dict[str, object]:
    checks: list[dict[str, str]] = []

    def add(level: str, message: str) -> None:
        checks.append({"level": level, "message": message})

    version = tuple(version_info or sys.version_info[:3])
    version_text = ".".join(str(part) for part in version[:3])
    if version < SUPPORTED_PYTHON_MIN or version >= SUPPORTED_PYTHON_MAX_EXCLUSIVE:
        add("FAIL", f"Python {version_text} は対象外です。3.11〜3.14を使用してください。")
    else:
        add("PASS", f"Python {version_text}")

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if path.is_file():
            add("PASS", f"{relative_path} を確認")
        else:
            add("FAIL", f"{relative_path} がありません。Clone / checkout状態を確認してください。")

    if _venv_exists(root):
        add("PASS", ".venv を確認")
    else:
        add("WARN", ".venv は未作成です。開発時は scripts/bootstrap を実行してください。")

    env_path = root / ".env"
    env = parse_env(env_path.read_text(encoding="utf-8")) if env_path.is_file() else {}
    if env_path.is_file():
        add("PASS", ".env を確認")
    else:
        add("WARN", ".env は未作成です。.env.example から作成できます。")

    data_value = env.get("APP_DATA_DIR", "data") or "data"
    data_dir = Path(data_value)
    if not data_dir.is_absolute():
        data_dir = root / data_dir

    if data_dir.exists() and not data_dir.is_dir():
        add("FAIL", f"APP_DATA_DIR がdirectoryではありません: {data_dir}")
    elif data_dir.is_dir() and not os.access(data_dir, os.W_OK):
        add("FAIL", f"APP_DATA_DIR へ書き込めません: {data_dir}")
    elif data_dir.is_dir():
        add("PASS", f"APP_DATA_DIR を確認: {data_dir}")
    else:
        add("WARN", f"APP_DATA_DIR は未作成です。アプリ起動時に作成されます: {data_dir}")

    for command in OPTIONAL_TOOLS:
        resolved = which(command)
        if resolved:
            add("PASS", f"{command} command: {resolved}")
        else:
            add(
                "WARN",
                f"{command} command が見つかりません。必要な機能を使う場合に導入してください。",
            )

    failed = any(check["level"] == "FAIL" for check in checks)
    return {"checks": checks, "failed": failed}


def run_doctor() -> int:
    result = diagnose()
    for check in result["checks"]:
        print(f"[{check['level']}] {check['message']}")
    failed = bool(result["failed"])
    print("Doctor: FAILED" if failed else "Doctor: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run_doctor())

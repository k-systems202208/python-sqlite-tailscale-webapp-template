import os
from pathlib import Path


LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _log_level(value: str | None) -> str:
    level = (value or "INFO").strip().upper() or "INFO"
    if level not in LOG_LEVELS:
        raise ValueError(f"LOG_LEVEL must be one of: {', '.join(sorted(LOG_LEVELS))}")
    return level


def load_settings() -> dict:
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = Path(os.getenv("APP_DATA_DIR", "data"))
    if not data_dir.is_absolute():
        data_dir = base_dir / data_dir

    return {
        "APP_NAME": os.getenv("APP_NAME", "Local Web App Template"),
        "APP_PORT": int(os.getenv("APP_PORT", "8000")),
        "APP_DATA_DIR": str(data_dir),
        "DATABASE": str(data_dir / "app.db"),
        "LOG_LEVEL": _log_level(os.getenv("LOG_LEVEL")),
        "LOCAL_OWNER_EMAIL": os.getenv("LOCAL_OWNER_EMAIL", "").strip(),
        "LOCAL_OWNER_NAME": os.getenv("LOCAL_OWNER_NAME", "Local Owner").strip(),
        "ALLOW_ANONYMOUS": _as_bool(os.getenv("ALLOW_ANONYMOUS"), False),
        "SECRET_KEY": os.getenv("APP_SECRET_KEY", "").strip() or None,
    }

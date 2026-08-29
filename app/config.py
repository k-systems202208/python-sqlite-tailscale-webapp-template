import os
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


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
        "LOCAL_OWNER_EMAIL": os.getenv("LOCAL_OWNER_EMAIL", "").strip(),
        "LOCAL_OWNER_NAME": os.getenv("LOCAL_OWNER_NAME", "Local Owner").strip(),
        "ALLOW_ANONYMOUS": _as_bool(os.getenv("ALLOW_ANONYMOUS"), False),
        "SECRET_KEY": os.getenv("APP_SECRET_KEY", "").strip() or None,
    }

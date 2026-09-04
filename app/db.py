import re
import sqlite3
from pathlib import Path

from flask import current_app, g

from .auth import Identity

MIGRATION_PATTERN = re.compile(r"^(?P<version>\d+)_(?P<name>[a-z0-9][a-z0-9_-]*)\.sql$")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        g.db = conn
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _migration_paths() -> list[Path]:
    app_dir = Path(__file__).resolve().parent
    paths = list((app_dir / "migrations").glob("*.sql"))
    paths.extend((app_dir / "features").glob("*/migrations/*.sql"))
    return sorted(paths, key=lambda path: path.as_posix())


def _migration_files() -> list[tuple[int, str, Path]]:
    migrations: list[tuple[int, str, Path]] = []
    versions: set[int] = set()

    for path in _migration_paths():
        match = MIGRATION_PATTERN.fullmatch(path.name)
        if not match:
            raise RuntimeError(f"Invalid migration filename: {path.name}")

        version = int(match.group("version"))
        name = match.group("name")
        if version in versions:
            raise RuntimeError(f"Duplicate migration version: {version}")
        versions.add(version)
        migrations.append((version, name, path))

    return sorted(migrations, key=lambda migration: migration[0])


def apply_migrations() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()

    applied = {
        row["version"]: row["name"]
        for row in db.execute("SELECT version, name FROM schema_migrations")
    }

    for version, name, path in _migration_files():
        if version in applied:
            if applied[version] != name:
                raise RuntimeError(
                    f"Migration {version} name changed from {applied[version]!r} to {name!r}"
                )
            continue

        sql = path.read_text(encoding="utf-8").strip()
        safe_name = name.replace("'", "''")
        script = (
            "BEGIN IMMEDIATE;\n"
            f"{sql}\n"
            "INSERT INTO schema_migrations (version, name) "
            f"VALUES ({version}, '{safe_name}');\n"
            "COMMIT;\n"
        )

        try:
            db.executescript(script)
        except Exception:
            db.rollback()
            raise


def init_db() -> None:
    apply_migrations()


def ensure_user(identity: Identity):
    db = get_db()
    db.execute(
        """
        INSERT INTO users (login, display_name, identity_source)
        VALUES (?, ?, ?)
        ON CONFLICT(login) DO UPDATE SET
            display_name = excluded.display_name,
            identity_source = excluded.identity_source,
            last_seen_at = CURRENT_TIMESTAMP
        """,
        (identity.login, identity.display_name, identity.source),
    )
    db.commit()
    return db.execute(
        "SELECT id, login, display_name, identity_source FROM users WHERE login = ?",
        (identity.login,),
    ).fetchone()

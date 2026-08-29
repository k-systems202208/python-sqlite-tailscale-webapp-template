import sqlite3
from pathlib import Path

from flask import current_app, g

from .auth import Identity


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


def init_db() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    db = get_db()
    db.executescript(schema_path.read_text(encoding="utf-8"))
    db.commit()


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

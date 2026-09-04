import sqlite3
from pathlib import Path

from app import create_app
from app.db import apply_migrations, get_db


ROOT = Path(__file__).resolve().parents[1]


def test_initial_migration_is_applied_once(app):
    with app.app_context():
        rows = get_db().execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        ).fetchall()
        assert [(row["version"], row["name"]) for row in rows] == [(1, "initial")]

        apply_migrations()

        count = get_db().execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 1


def test_existing_schema_is_baselined_without_data_loss(tmp_path):
    database = tmp_path / "existing.db"
    migration_sql = (ROOT / "app" / "migrations" / "001_initial.sql").read_text(
        encoding="utf-8"
    )

    with sqlite3.connect(database) as connection:
        connection.executescript(migration_sql)
        connection.execute(
            "INSERT INTO users (login, display_name, identity_source) VALUES (?, ?, ?)",
            ("existing@example.com", "Existing", "local"),
        )
        connection.commit()

    app = create_app(
        {
            "TESTING": True,
            "APP_DATA_DIR": str(tmp_path),
            "DATABASE": str(database),
            "SECRET_KEY": "test-secret",
            "LOCAL_OWNER_EMAIL": "",
            "ALLOW_ANONYMOUS": False,
        }
    )

    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 1

import sqlite3

from app import create_app
from app.db import _migration_files, apply_migrations, get_db

LEGACY_V1_SQL = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    identity_source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 200),
    body TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'done')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_items_owner_updated
    ON items(owner_user_id, updated_at DESC, id DESC);
"""


def test_core_and_sample_migrations_are_applied_once(app):
    with app.app_context():
        rows = (
            get_db()
            .execute("SELECT version, name FROM schema_migrations ORDER BY version")
            .fetchall()
        )
        assert [(row["version"], row["name"]) for row in rows] == [
            (1, "initial"),
            (2, "sample_items"),
        ]

        apply_migrations()

        count = get_db().execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 2


def test_sample_migration_is_discovered_from_feature_directory(app):
    with app.app_context():
        migrations = _migration_files()

    assert migrations[0][2].as_posix().endswith("app/migrations/001_initial.sql")
    assert migrations[1][2].as_posix().endswith(
        "app/features/items/migrations/002_sample_items.sql"
    )


def test_legacy_version1_database_gets_sample_marker_without_data_loss(tmp_path):
    database = tmp_path / "legacy.db"

    with sqlite3.connect(database) as connection:
        connection.executescript(LEGACY_V1_SQL)
        connection.execute(
            """
            CREATE TABLE schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (1, 'initial')"
        )
        user_id = connection.execute(
            "INSERT INTO users (login, display_name, identity_source) VALUES (?, ?, ?)",
            ("existing@example.com", "Existing", "local"),
        ).lastrowid
        connection.execute(
            "INSERT INTO items (owner_user_id, title, body) VALUES (?, ?, ?)",
            (user_id, "Existing item", "must survive"),
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
        assert db.execute("SELECT title FROM items").fetchone()[0] == "Existing item"
        rows = db.execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        ).fetchall()
        assert [(row["version"], row["name"]) for row in rows] == [
            (1, "initial"),
            (2, "sample_items"),
        ]

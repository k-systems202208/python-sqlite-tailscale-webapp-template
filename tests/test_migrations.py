from pathlib import Path

import app.db as db_module
from app import create_app


def test_core_migration_is_always_discovered():
    migrations = db_module._migration_files()

    version, name, path = migrations[0]
    assert (version, name) == (1, "initial")
    assert path.as_posix().endswith("app/migrations/001_initial.sql")


def test_core_migration_is_applied_once_without_feature_migrations(monkeypatch, tmp_path):
    core_migration = Path(db_module.__file__).with_name("migrations") / "001_initial.sql"
    monkeypatch.setattr(db_module, "_migration_paths", lambda: [core_migration])

    webapp = create_app(
        {
            "TESTING": True,
            "APP_DATA_DIR": str(tmp_path),
            "DATABASE": str(tmp_path / "core-migration.db"),
            "SECRET_KEY": "test-secret",
            "LOCAL_OWNER_EMAIL": "",
            "ALLOW_ANONYMOUS": False,
        }
    )

    with webapp.app_context():
        rows = (
            db_module.get_db()
            .execute("SELECT version, name FROM schema_migrations ORDER BY version")
            .fetchall()
        )
        assert [(row["version"], row["name"]) for row in rows] == [(1, "initial")]

        db_module.apply_migrations()

        count = db_module.get_db().execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert count == 1

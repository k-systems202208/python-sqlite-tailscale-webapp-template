from pathlib import Path

from flask import Flask

from app import create_app
import app.db as db_module
import app.features as features
from conftest import tailscale_headers


def test_feature_registration_is_safe_when_no_feature_package_exists(monkeypatch):
    webapp = Flask(__name__)
    monkeypatch.setattr(features, "feature_names", lambda: [])

    features.register_features(webapp)

    assert list(webapp.blueprints) == []


def test_core_app_works_without_sample_feature(monkeypatch, tmp_path):
    core_migration = Path(db_module.__file__).with_name("migrations") / "001_initial.sql"
    monkeypatch.setattr(features, "feature_names", lambda: [])
    monkeypatch.setattr(db_module, "_migration_paths", lambda: [core_migration])

    webapp = create_app(
        {
            "TESTING": True,
            "APP_NAME": "Core Only",
            "APP_DATA_DIR": str(tmp_path),
            "DATABASE": str(tmp_path / "core-only.db"),
            "SECRET_KEY": "test-secret",
            "LOCAL_OWNER_EMAIL": "",
            "LOCAL_OWNER_NAME": "",
            "ALLOW_ANONYMOUS": False,
        }
    )
    client = webapp.test_client()
    alice = tailscale_headers()

    assert client.get("/", headers=alice).status_code == 200
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200
    assert client.get("/api/me", headers=alice).status_code == 200
    assert client.get("/items", headers=alice).status_code == 404

    with webapp.app_context():
        tables = {
            row[0]
            for row in db_module.get_db()
            .execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            .fetchall()
        }
        assert "users" in tables
        assert "items" not in tables

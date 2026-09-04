import sqlite3

import app.features as features
from app import create_app
from app.db import _migration_files, get_db
from conftest import csrf_for, tailscale_headers

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


def test_items_sample_is_discovered_as_feature():
    assert "items" in features.feature_names()


def test_sample_migration_is_discovered_from_feature_directory(app):
    with app.app_context():
        migrations = _migration_files()

    assert any(
        version == 2
        and name == "sample_items"
        and path.as_posix().endswith(
            "app/features/items/migrations/002_sample_items.sql"
        )
        for version, name, path in migrations
    )


def test_items_sample_page_is_separate_from_core_home(client):
    alice = tailscale_headers()
    assert client.get("/", headers=alice).status_code == 200
    assert client.get("/items", headers=alice).status_code == 200


def test_items_are_isolated_per_user(client):
    alice = tailscale_headers("alice@example.com", "Alice")
    bob = tailscale_headers("bob@example.com", "Bob")

    token = csrf_for(client, alice)
    created = client.post(
        "/api/items",
        json={"title": "Alice private item", "body": "secret-ish app data"},
        headers={**alice, "X-CSRF-Token": token},
    )
    assert created.status_code == 201

    alice_items = client.get("/api/items", headers=alice).get_json()
    bob_items = client.get("/api/items", headers=bob).get_json()

    assert [item["title"] for item in alice_items] == ["Alice private item"]
    assert bob_items == []


def test_api_validation_error_is_json(client):
    alice = tailscale_headers()
    token = csrf_for(client, alice)
    response = client.post(
        "/api/items",
        json={"title": ""},
        headers={**alice, "X-CSRF-Token": token},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == 400
    assert "between 1 and 200" in payload["error"]


def test_mutation_requires_csrf(client):
    alice = tailscale_headers()
    response = client.post(
        "/api/items",
        json={"title": "Should fail"},
        headers=alice,
    )
    assert response.status_code == 400


def test_toggle_and_delete_item(client):
    alice = tailscale_headers()
    token = csrf_for(client, alice)
    created = client.post(
        "/api/items",
        json={"title": "Toggle me"},
        headers={**alice, "X-CSRF-Token": token},
    )
    item_id = created.get_json()["id"]

    toggled = client.post(
        f"/items/{item_id}/toggle",
        data={"csrf_token": token},
        headers=alice,
    )
    assert toggled.status_code == 302
    assert client.get("/api/items", headers=alice).get_json()[0]["status"] == "done"

    deleted = client.post(
        f"/items/{item_id}/delete",
        data={"csrf_token": token},
        headers=alice,
    )
    assert deleted.status_code == 302
    assert client.get("/api/items", headers=alice).get_json() == []


def test_other_user_cannot_mutate_item(client):
    alice = tailscale_headers("alice@example.com", "Alice")
    bob = tailscale_headers("bob@example.com", "Bob")
    alice_token = csrf_for(client, alice)
    created = client.post(
        "/api/items",
        json={"title": "Alice only"},
        headers={**alice, "X-CSRF-Token": alice_token},
    )
    item_id = created.get_json()["id"]

    bob_token = csrf_for(client, bob)
    response = client.post(
        f"/items/{item_id}/delete",
        data={"csrf_token": bob_token},
        headers=bob,
    )
    assert response.status_code == 404
    assert len(client.get("/api/items", headers=alice).get_json()) == 1


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

    webapp = create_app(
        {
            "TESTING": True,
            "APP_DATA_DIR": str(tmp_path),
            "DATABASE": str(database),
            "SECRET_KEY": "test-secret",
            "LOCAL_OWNER_EMAIL": "",
            "ALLOW_ANONYMOUS": False,
        }
    )

    with webapp.app_context():
        db = get_db()
        assert db.execute("SELECT title FROM items").fetchone()[0] == "Existing item"
        rows = db.execute(
            "SELECT version, name FROM schema_migrations ORDER BY version"
        ).fetchall()
        assert [(row["version"], row["name"]) for row in rows] == [
            (1, "initial"),
            (2, "sample_items"),
        ]

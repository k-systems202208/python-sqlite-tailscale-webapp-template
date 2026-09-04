import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "APP_NAME": "Test App",
            "APP_DATA_DIR": str(tmp_path),
            "DATABASE": str(tmp_path / "test.db"),
            "SECRET_KEY": "test-secret",
            "LOCAL_OWNER_EMAIL": "",
            "LOCAL_OWNER_NAME": "",
            "ALLOW_ANONYMOUS": False,
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()


def tailscale_headers(login="alice@example.com", name="Alice"):
    return {
        "Tailscale-User-Login": login,
        "Tailscale-User-Name": name,
    }


def csrf_for(client, headers):
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    with client.session_transaction() as session:
        return session["_csrf_token"]

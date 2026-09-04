from conftest import csrf_for, tailscale_headers


def test_readiness_checks_database(client):
    response = client.get("/readyz", environ_base={"REMOTE_ADDR": "192.0.2.10"})
    assert response.status_code == 200
    assert response.get_json() == {"status": "ready", "database": "ok"}


def test_api_authentication_error_is_json(client):
    response = client.get("/api/me", environ_base={"REMOTE_ADDR": "192.0.2.10"})
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["status"] == 401
    assert "error" in payload


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

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

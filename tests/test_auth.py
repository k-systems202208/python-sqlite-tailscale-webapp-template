from conftest import tailscale_headers


def test_tailscale_identity_is_accepted_from_loopback(client):
    response = client.get("/api/me", headers=tailscale_headers())
    assert response.status_code == 200
    assert response.get_json()["login"] == "alice@example.com"
    assert response.get_json()["source"] == "tailscale"


def test_spoofed_tailscale_headers_are_rejected_from_non_loopback(client):
    response = client.get(
        "/api/me",
        headers=tailscale_headers(),
        environ_base={"REMOTE_ADDR": "192.0.2.10"},
    )
    assert response.status_code == 401


def test_health_check_does_not_require_identity(client):
    response = client.get("/healthz", environ_base={"REMOTE_ADDR": "192.0.2.10"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

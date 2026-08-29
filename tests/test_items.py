from conftest import csrf_for, tailscale_headers


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


def test_mutation_requires_csrf(client):
    alice = tailscale_headers()
    response = client.post(
        "/api/items",
        json={"title": "Should fail"},
        headers=alice,
    )
    assert response.status_code == 400

from conftest import csrf_for, tailscale_headers


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

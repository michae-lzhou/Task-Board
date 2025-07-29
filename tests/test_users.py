# tests/test_users.py
def test_create_and_get_user(client):
    resp = client.post("/users/", json={"name": "Alice", "email": "alice@a.com"})
    assert resp.status_code == 200
    user = resp.json()
    assert user["email"] == "alice@a.com"
    # Get by ID
    resp = client.get(f"/users/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@a.com"

def test_create_duplicate_user_email(client):
    client.post("/users/", json={"name": "Bob", "email": "bob@b.com"})
    resp = client.post("/users/", json={"name": "Bobby", "email": "bob@b.com"})
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()

def test_get_nonexistent_user(client):
    resp = client.get("/users/99999")
    assert resp.status_code == 404

def test_read_all_users(client):
    client.post("/users/", json={"name": "Charlie", "email": "charlie@c.com"})
    resp = client.get("/users/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert any(u["email"] == "charlie@c.com" for u in resp.json())

def test_delete_user(client):
    user = client.post("/users/", json={"name": "Dave",
                       "email": "dave@d.com"}).json()
    resp = client.delete(f"/users/{user['id']}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()
    # Confirm deletion
    resp = client.get(f"/users/{user['id']}")
    assert resp.status_code == 404

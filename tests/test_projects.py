# tests/test_projects.py
def test_create_and_get_project(client):
    # Create
    resp = client.post("/projects/", json={"name": "Alpha"})
    assert resp.status_code == 200
    project = resp.json()
    assert project["name"] == "Alpha"
    # Get by ID
    resp = client.get(f"/projects/{project['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alpha"

def test_create_duplicate_project(client):
    client.post("/projects/", json={"name": "Beta"})
    resp = client.post("/projects/", json={"name": "Beta"})
    assert resp.status_code == 400
    assert "duplicate" in resp.json()["detail"].lower()

def test_get_nonexistent_project(client):
    resp = client.get("/projects/99999")
    assert resp.status_code == 404

def test_read_all_projects(client):
    client.post("/projects/", json={"name": "Gamma"})
    client.post("/projects/", json={"name": "Delta"})
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 2

def test_delete_project(client):
    resp = client.post("/projects/", json={"name": "Epsilon"})
    pid = resp.json()["id"]
    resp = client.delete(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()
    # Confirm deletion
    resp = client.get(f"/projects/{pid}")
    assert resp.status_code == 404

def test_add_and_remove_member(client):
    # Create project and user
    project = client.post("/projects/", json={"name": "Zeta"}).json()
    user = client.post("/users/", json={"name": "Zed",
                       "email": "zed@example.com"}).json()
    # Add member
    resp = client.post(f"/projects/{project['id']}/add-member",
                       json={"name": "Zed", "email": "zed@example.com"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "zed@example.com"
    # Remove member
    resp = client.post(f"/projects/{project['id']}/remove-member",
                       json={"name": "Zed", "email": "zed@example.com"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "zed@example.com"

def test_add_member_duplicate_email(client):
    project = client.post("/projects/", json={"name": "Eta"}).json()
    client.post("/users/", json={"name": "Eve", "email": "eve@example.com"})
    # Add member first time
    client.post(f"/projects/{project['id']}/add-member", json={"name": "Eve",
                "email": "eve@example.com"})
    # Add again (should fail with UserInProject)
    resp = client.post(f"/projects/{project['id']}/add-member",
                       json={"name": "Eve", "email": "eve@example.com"})
    assert resp.status_code == 400
    assert "already" in resp.json()["detail"].lower()

def test_remove_non_member(client):
    project = client.post("/projects/", json={"name": "Theta"}).json()
    client.post("/users/", json={"name": "Tom", "email": "tom@example.com"})
    resp = client.post(f"/projects/{project['id']}/remove-member",
                       json={"name": "Tom", "email": "tom@example.com"})
    assert resp.status_code == 400
    assert "not a member" in resp.json()["detail"].lower()

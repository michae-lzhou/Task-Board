# tests/test_tasks.py
def test_create_and_get_task(client):
    # Create project
    project = client.post("/projects/", json={"name": "TaskProj"}).json()
    # Create task
    resp = client.post("/tasks/", json={
        "title": "Task1",
        "description": "desc",
        "project_id": project["id"],
        "assignee_id": None
    })
    assert resp.status_code == 200
    task = resp.json()
    assert task["title"] == "Task1"
    # Get by ID
    resp = client.get(f"/tasks/{task['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Task1"

def test_create_task_no_project(client):
    resp = client.post("/tasks/", json={
        "title": "NoProjTask",
        "description": "desc",
        "project_id": 9999,
        "assignee_id": None
    })
    assert resp.status_code == 404

def test_create_duplicate_task_name(client):
    project = client.post("/projects/", json={"name": "DupTaskProj"}).json()
    client.post("/tasks/", json={
        "title": "DupTask",
        "description": "desc",
        "project_id": project["id"],
        "assignee_id": None
    })
    resp = client.post("/tasks/", json={
        "title": "DupTask",
        "description": "desc",
        "project_id": project["id"],
        "assignee_id": None
    })
    assert resp.status_code == 400
    assert "duplicate" in resp.json()["detail"].lower()

def test_update_task(client):
    project = client.post("/projects/", json={"name": "UpdateTaskProj"}).json()
    task = client.post("/tasks/", json={
        "title": "ToUpdate",
        "description": "desc",
        "project_id": project["id"],
        "assignee_id": None
    }).json()
    # Update task
    resp = client.put(f"/tasks/{task['id']}", json={
        "title": "UpdatedTitle",
        "description": "newdesc",
        "project_id": project["id"],
        "assignee_id": None
    })
    assert resp.status_code == 200
    assert resp.json()["title"] == "UpdatedTitle"

def test_delete_task(client):
    project = client.post("/projects/", json={"name": "DeleteTaskProj"}).json()
    task = client.post("/tasks/", json={
        "title": "ToDelete",
        "description": "desc",
        "project_id": project["id"],
        "assignee_id": None
    }).json()
    resp = client.delete(f"/tasks/{task['id']}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()
    # Confirm deletion
    resp = client.get(f"/tasks/{task['id']}")
    assert resp.status_code == 404

# tests/test_integration_edge_cases.py
def test_full_integration_edge_cases(client):
    # 1. Create a project and a user
    project_resp = client.post("/projects/", json={"name": "EdgeProj"})
    assert project_resp.status_code == 200
    project = project_resp.json()

    user_resp = client.post("/users/", json={"name": "EdgeUser",
                                             "email": "edgeuser@example.com"})
    assert user_resp.status_code == 200
    user = user_resp.json()

    # 2. Add user to project
    add_member_resp = client.post(
        f"/projects/{project['id']}/add-member",
        json={"name": "EdgeUser", "email": "edgeuser@example.com"}
    )
    assert add_member_resp.status_code == 200

    # 3. Try to add the same user again (should fail)
    add_member_again = client.post(
        f"/projects/{project['id']}/add-member",
        json={"name": "EdgeUser", "email": "edgeuser@example.com"}
    )
    assert add_member_again.status_code == 400
    assert "already" in add_member_again.json()["detail"].lower()

    # 4. Try to add a user with the same email but different name
    #    (should fail at user creation)
    dup_email_resp = client.post("/users/", json={"name": "OtherName",
                                 "email": "edgeuser@example.com"})
    assert dup_email_resp.status_code == 400

    # 5. Create a second user and add to project
    user2_resp = client.post("/users/", json={"name": "EdgeUser2",
                             "email": "edgeuser2@example.com"})
    assert user2_resp.status_code == 200
    user2 = user2_resp.json()
    add_member2_resp = client.post(
        f"/projects/{project['id']}/add-member",
        json={"name": "EdgeUser2", "email": "edgeuser2@example.com"}
    )
    assert add_member2_resp.status_code == 200

    # 6. Create a task assigned to user1
    task_resp = client.post("/tasks/", json={
        "title": "EdgeTask",
        "description": "Edge case task",
        "project_id": project["id"],
        "assigned_to": user["id"]
    })
    assert task_resp.status_code == 200
    task = task_resp.json()

    # 7. Try to create a task with the same name in the same project
    #    (should fail)
    dup_task_resp = client.post("/tasks/", json={
        "title": "EdgeTask",
        "description": "Duplicate",
        "project_id": project["id"],
        "assigned_to": user["id"]
    })
    assert dup_task_resp.status_code == 400

    # 8. Try to assign a task to a user not in the project (should fail)
    outsider_resp = client.post("/users/", json={"name": "Outsider",
                                "email": "outsider@example.com"})
    outsider = outsider_resp.json()
    task_assign_fail = client.post("/tasks/", json={
        "title": "OutsiderTask",
        "description": "Should fail",
        "project_id": project["id"],
        "assigned_to": outsider["id"]
    })
    assert task_assign_fail.status_code == 400 or
           task_assign_fail.status_code == 404

    # 9. Remove user1 from project (should succeed)
    remove_member_resp = client.post(
        f"/projects/{project['id']}/remove-member",
        json={"name": "EdgeUser", "email": "edgeuser@example.com"}
    )
    assert remove_member_resp.status_code == 200

    # 10. Try to remove user1 again (should fail)
    remove_member_again = client.post(
        f"/projects/{project['id']}/remove-member",
        json={"name": "EdgeUser", "email": "edgeuser@example.com"}
    )
    assert remove_member_again.status_code == 400

    # 11. Try to assign a task to a user who was removed from the project
    #     (should fail)
    update_task_resp = client.put(f"/tasks/{task['id']}", json={
        "title": "EdgeTask",
        "description": "Reassigned",
        "project_id": project["id"],
        "assigned_to": user["id"]
    })
    assert update_task_resp.status_code == 400 or
           update_task_resp.status_code == 404

    # 12. Remove user2 from project, then delete user2 (should succeed)
    client.post(
        f"/projects/{project['id']}/remove-member",
        json={"name": "EdgeUser2", "email": "edgeuser2@example.com"}
    )
    del_user2_resp = client.delete(f"/users/{user2['id']}")
    assert del_user2_resp.status_code == 200

    # 13. Try to delete a user that doesn't exist
    del_nonexistent_user = client.delete("/users/99999")
    assert del_nonexistent_user.status_code == 404

    # 14. Try to delete a project that doesn't exist
    del_nonexistent_project = client.delete("/projects/99999")
    assert del_nonexistent_project.status_code == 404

    # 15. Try to get tasks for a non-existent project
    get_tasks_nonexistent = client.get("/projects/99999/tasks")
    assert get_tasks_nonexistent.status_code == 404

    # 16. Try to get users for a non-existent project
    get_users_nonexistent = client.get("/projects/99999/users")
    assert get_users_nonexistent.status_code == 404

    # 17. Delete the project
    del_project_resp = client.delete(f"/projects/{project['id']}")
    assert del_project_resp.status_code == 200

    # 18. Try to get the deleted project
    get_deleted_project = client.get(f"/projects/{project['id']}")
    assert get_deleted_project.status_code == 404

    # 19. Try to create a task in a deleted project
    task_in_deleted_project = client.post("/tasks/", json={
        "title": "ShouldFail",
        "description": "No project",
        "project_id": project["id"],
        "assigned_to": None
    })
    assert task_in_deleted_project.status_code == 404

    # 20. Try to update a deleted task
    update_deleted_task = client.put(f"/tasks/{task['id']}", json={
        "title": "ShouldFail",
        "description": "No task",
        "project_id": project["id"],
        "assigned_to": None
    })
    assert update_deleted_task.status_code == 404

    # 21. Try to delete a deleted task
    del_deleted_task = client.delete(f"/tasks/{task['id']}")
    assert del_deleted_task.status_code == 404

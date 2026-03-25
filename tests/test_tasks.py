import pytest


class TestGetTasks:
    def test_get_tasks_empty(self, client, auth_headers):
        response = client.get("/api/tasks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["tasks"] == []
        assert data["total"] == 0

    def test_get_tasks_unauthorized(self, client):
        response = client.get("/api/tasks/")
        assert response.status_code == 401

    def test_get_tasks_with_status_filter(self, client, auth_headers):
        client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Pending task",
            "status": "pending",
        })
        response = client.get("/api/tasks/?status=pending", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.get_json()["tasks"]) == 1

    def test_get_tasks_invalid_status(self, client, auth_headers):
        response = client.get("/api/tasks/?status=invalid", headers=auth_headers)
        assert response.status_code == 422

    def test_get_tasks_with_priority_filter(self, client, auth_headers):
        client.post("/api/tasks/", headers=auth_headers, json={
            "title": "High priority task",
            "priority": "high",
        })
        response = client.get("/api/tasks/?priority=high", headers=auth_headers)
        assert response.status_code == 200

    def test_get_tasks_invalid_priority(self, client, auth_headers):
        response = client.get("/api/tasks/?priority=extreme", headers=auth_headers)
        assert response.status_code == 422

    def test_get_tasks_pagination(self, client, auth_headers):
        for i in range(5):
            client.post("/api/tasks/", headers=auth_headers,
                        json={"title": f"Task {i}"})
        response = client.get("/api/tasks/?per_page=2&page=1",
                               headers=auth_headers)
        data = response.get_json()
        assert len(data["tasks"]) == 2
        assert data["total"] == 5

    def test_get_tasks_per_page_capped(self, client, auth_headers):
        response = client.get("/api/tasks/?per_page=999", headers=auth_headers)
        assert response.status_code == 200


class TestCreateTask:
    def test_create_task_success(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Test Task",
            "description": "A test task",
            "priority": "high",
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["task"]["title"] == "Test Task"
        assert data["task"]["priority"] == "high"
        assert data["task"]["status"] == "pending"

    def test_create_task_no_data(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers)
        assert response.status_code == 400

    def test_create_task_missing_title(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "description": "No title here",
        })
        assert response.status_code == 422

    def test_create_task_empty_title(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "   ",
        })
        assert response.status_code == 422

    def test_create_task_invalid_status(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Bad status task",
            "status": "unknown",
        })
        assert response.status_code == 422

    def test_create_task_invalid_priority(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Bad priority task",
            "priority": "extreme",
        })
        assert response.status_code == 422

    def test_create_task_with_due_date(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Dated Task",
            "due_date": "2025-12-31T23:59:59",
        })
        assert response.status_code == 201
        assert response.get_json()["task"]["due_date"] is not None

    def test_create_task_invalid_due_date(self, client, auth_headers):
        response = client.post("/api/tasks/", headers=auth_headers, json={
            "title": "Bad date task",
            "due_date": "not-a-date",
        })
        assert response.status_code == 422

    def test_create_task_unauthorized(self, client):
        response = client.post("/api/tasks/", json={"title": "Task"})
        assert response.status_code == 401


class TestGetSingleTask:
    def test_get_task_success(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Single task"})
        task_id = create.get_json()["task"]["id"]
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["task"]["title"] == "Single task"

    def test_get_task_not_found(self, client, auth_headers):
        response = client.get("/api/tasks/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_task_other_user(self, client, auth_headers, second_user_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "User 1 task"})
        task_id = create.get_json()["task"]["id"]
        response = client.get(f"/api/tasks/{task_id}",
                               headers=second_user_headers)
        assert response.status_code == 404


class TestUpdateTask:
    def test_update_task_success(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Original"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"title": "Updated", "status": "in_progress"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["task"]["title"] == "Updated"
        assert data["task"]["status"] == "in_progress"

    def test_update_task_not_found(self, client, auth_headers):
        response = client.put("/api/tasks/9999", headers=auth_headers,
                               json={"title": "Updated"})
        assert response.status_code == 404

    def test_update_task_no_data(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Original"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 400

    def test_update_task_empty_title(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Original"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"title": ""})
        assert response.status_code == 422

    def test_update_task_invalid_status(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Original"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"status": "invalid"})
        assert response.status_code == 422

    def test_update_task_invalid_priority(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Original"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"priority": "critical"})
        assert response.status_code == 422

    def test_update_task_clear_due_date(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Task", "due_date": "2025-12-31T00:00:00"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"due_date": None})
        assert response.status_code == 200
        assert response.get_json()["task"]["due_date"] is None

    def test_update_task_invalid_due_date(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Task"})
        task_id = create.get_json()["task"]["id"]
        response = client.put(f"/api/tasks/{task_id}", headers=auth_headers,
                               json={"due_date": "bad-date"})
        assert response.status_code == 422


class TestDeleteTask:
    def test_delete_task_success(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Delete me"})
        task_id = create.get_json()["task"]["id"]
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        get = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert get.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        response = client.delete("/api/tasks/9999", headers=auth_headers)
        assert response.status_code == 404


class TestCompleteTask:
    def test_complete_task(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Complete me"})
        task_id = create.get_json()["task"]["id"]
        response = client.patch(f"/api/tasks/{task_id}/complete",
                                 headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["task"]["status"] == "completed"

    def test_complete_task_not_found(self, client, auth_headers):
        response = client.patch("/api/tasks/9999/complete", headers=auth_headers)
        assert response.status_code == 404


class TestTaskStats:
    def test_get_stats_empty(self, client, auth_headers):
        response = client.get("/api/tasks/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_tasks"] == 0
        assert data["completion_rate"] == 0

    def test_get_stats_with_tasks(self, client, auth_headers):
        client.post("/api/tasks/", headers=auth_headers,
                    json={"title": "T1", "priority": "high"})
        t2 = client.post("/api/tasks/", headers=auth_headers,
                         json={"title": "T2", "priority": "low"})
        t2_id = t2.get_json()["task"]["id"]
        client.patch(f"/api/tasks/{t2_id}/complete", headers=auth_headers)

        response = client.get("/api/tasks/stats", headers=auth_headers)
        data = response.get_json()
        assert data["total_tasks"] == 2
        assert data["completion_rate"] == 50.0


class TestTaskComments:
    def test_add_comment(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Commented task"})
        task_id = create.get_json()["task"]["id"]
        response = client.post(f"/api/tasks/{task_id}/comments",
                                headers=auth_headers,
                                json={"content": "First comment"})
        assert response.status_code == 201

    def test_get_comments(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Task with comments"})
        task_id = create.get_json()["task"]["id"]
        client.post(f"/api/tasks/{task_id}/comments", headers=auth_headers,
                    json={"content": "Comment A"})
        response = client.get(f"/api/tasks/{task_id}/comments",
                               headers=auth_headers)
        assert response.status_code == 200
        assert len(response.get_json()["comments"]) == 1

    def test_add_empty_comment(self, client, auth_headers):
        create = client.post("/api/tasks/", headers=auth_headers,
                             json={"title": "Task"})
        task_id = create.get_json()["task"]["id"]
        response = client.post(f"/api/tasks/{task_id}/comments",
                                headers=auth_headers,
                                json={"content": ""})
        assert response.status_code == 400

    def test_comment_on_nonexistent_task(self, client, auth_headers):
        response = client.post("/api/tasks/9999/comments",
                                headers=auth_headers,
                                json={"content": "Comment"})
        assert response.status_code == 404

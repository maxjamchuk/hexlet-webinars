def test_get_tasks(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.get_json()) == 2
    assert response.get_json()[0]["title"] == "Learn pytest"


def test_get_existing_task(client):
    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_missing_task(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Task 999 not found"}


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Learn test client"})

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Learn test client",
        "completed": False,
    }


def test_create_task_with_invalid_payload(client):
    response = client.post("/tasks", json={"completed": False})

    assert response.status_code == 400
    assert response.get_json() == {"error": "title is required"}


def test_update_task(client):
    response = client.patch("/tasks/1", json={"completed": True})

    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_update_missing_task(client):
    response = client.patch("/tasks/999", json={"completed": True})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Task 999 not found"}


def test_update_task_with_invalid_payload(client):
    response = client.patch("/tasks/1", json={"completed": "yes"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "completed must be a boolean"}


def test_delete_task(client):
    response = client.delete("/tasks/1")

    assert response.status_code == 204
    assert response.data == b""


def test_delete_missing_task(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Task 999 not found"}

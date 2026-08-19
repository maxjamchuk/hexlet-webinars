from fastapi.testclient import TestClient

VALID_INCIDENT = {
    "title": "Капибара телепортируется между переговорками",
    "description": "Исчезает у доски и появляется возле кофемашины",
    "category": "creature",
    "danger_level": 4,
}


def create_incident(client: TestClient) -> int:
    response = client.post("/incidents", json=VALID_INCIDENT)
    assert response.status_code == 201
    return response.json()["id"]


def test_create_incident(client: TestClient) -> None:
    response = client.post("/incidents", json=VALID_INCIDENT)

    assert response.status_code == 201
    assert response.json()["status"] == "new"
    assert response.json()["id"] == 1


def test_invalid_incident_returns_422(client: TestClient) -> None:
    response = client.post(
        "/incidents",
        json={**VALID_INCIDENT, "title": "Ой", "danger_level": 8},
    )

    assert response.status_code == 422


def test_missing_incident_returns_404(client: TestClient) -> None:
    response = client.get("/incidents/999")

    assert response.status_code == 404


def test_update_incident(client: TestClient) -> None:
    incident_id = create_incident(client)

    response = client.patch(
        f"/incidents/{incident_id}",
        json={"status": "investigating"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "investigating"
    assert response.json()["title"] == VALID_INCIDENT["title"]


def test_delete_incident(client: TestClient) -> None:
    incident_id = create_incident(client)

    response = client.delete(f"/incidents/{incident_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/incidents/{incident_id}").status_code == 404

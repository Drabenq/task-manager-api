from datetime import date, timedelta

import pytest


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_task_with_defaults(client):
    response = client.post("/tasks", json={"title": "Buy milk"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "Buy milk"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["due_date"] is None


def test_create_task_trims_title(client):
    response = client.post("/tasks", json={"title": "   Review PR   "})
    assert response.json()["title"] == "Review PR"


def test_create_task_with_all_fields(client):
    due = (date.today() + timedelta(days=3)).isoformat()
    payload = {"title": "Deploy", "description": "v1.2", "priority": "high", "due_date": due}

    body = client.post("/tasks", json=payload).json()

    assert body["description"] == "v1.2"
    assert body["priority"] == "high"
    assert body["due_date"] == due


@pytest.mark.parametrize(
    "payload, reason",
    [
        ({}, "missing title"),
        ({"title": ""}, "empty title"),
        ({"title": "    "}, "blank title"),
        ({"title": "x" * 121}, "title too long"),
        ({"title": "ok", "priority": "urgent"}, "invalid priority"),
        ({"title": "ok", "due_date": "not-a-date"}, "invalid date format"),
        ({"title": "ok", "due_date": (date.today() - timedelta(days=1)).isoformat()}, "past due date"),
    ],
)
def test_create_task_rejects_invalid_payload(client, payload, reason):
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422, reason

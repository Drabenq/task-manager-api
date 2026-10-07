from datetime import date, timedelta


def test_partial_update_only_changes_sent_fields(client, make_task):
    task = make_task(title="Original", priority="low")

    response = client.patch(f"/tasks/{task['id']}", json={"status": "done"})

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "done"
    assert body["title"] == "Original"
    assert body["priority"] == "low"


def test_update_rejects_blank_title(client, make_task):
    task = make_task()
    assert client.patch(f"/tasks/{task['id']}", json={"title": "  "}).status_code == 422


def test_update_rejects_invalid_status(client, make_task):
    task = make_task()
    assert client.patch(f"/tasks/{task['id']}", json={"status": "archived"}).status_code == 422


def test_update_unknown_task_returns_404(client):
    assert client.patch("/tasks/9999", json={"title": "x"}).status_code == 404


def test_delete_task(client, make_task):
    task = make_task()

    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_delete_unknown_task_returns_404(client):
    assert client.delete("/tasks/9999").status_code == 404


def test_stats(client, make_task):
    make_task(title="a")
    late = make_task(title="b")
    finished = make_task(title="c")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    # Past dates are only rejected on creation; rescheduling into the past makes a task overdue.
    client.patch(f"/tasks/{late['id']}", json={"due_date": yesterday, "status": "in_progress"})
    client.patch(f"/tasks/{finished['id']}", json={"due_date": yesterday, "status": "done"})

    stats = client.get("/tasks/stats").json()

    assert stats == {"total": 3, "todo": 1, "in_progress": 1, "done": 1, "overdue": 1}

def test_get_task_by_id(client, make_task):
    task = make_task(title="Read docs")
    response = client.get(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json() == task


def test_get_unknown_task_returns_404(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 9999 not found"


def test_get_task_with_invalid_id_returns_422(client):
    assert client.get("/tasks/abc").status_code == 422


def test_list_is_empty_initially(client):
    assert client.get("/tasks").json() == []


def test_filter_by_priority(client, make_task):
    make_task(title="a", priority="low")
    make_task(title="b", priority="high")

    titles = [t["title"] for t in client.get("/tasks", params={"priority": "high"}).json()]
    assert titles == ["b"]


def test_filter_by_status(client, make_task):
    task = make_task(title="started")
    make_task(title="pending")
    client.patch(f"/tasks/{task['id']}", json={"status": "in_progress"})

    titles = [t["title"] for t in client.get("/tasks", params={"status": "in_progress"}).json()]
    assert titles == ["started"]


def test_search_is_case_insensitive_and_checks_description(client, make_task):
    make_task(title="Fix LOGIN bug")
    make_task(title="Other", description="related to login page")
    make_task(title="Unrelated")

    results = client.get("/tasks", params={"q": "login"}).json()
    assert len(results) == 2


def test_pagination(client, make_task):
    for i in range(5):
        make_task(title=f"task {i}")

    page = client.get("/tasks", params={"skip": 2, "limit": 2}).json()
    assert [t["title"] for t in page] == ["task 2", "task 3"]


def test_pagination_limit_is_capped(client):
    assert client.get("/tasks", params={"limit": 101}).status_code == 422

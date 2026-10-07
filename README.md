# Task Manager API

![CI](https://github.com/Drabenq/task-manager-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

REST API to create, filter and track tasks. Built with **FastAPI**, **SQLAlchemy 2.0** and **Pydantic v2**, covered by **pytest** with a 90% coverage gate, and shipped as a **Docker** image that CI smoke-tests on every push.

## Features

- Full CRUD for tasks with partial updates (`PATCH` only changes the fields you send)
- Filters by status and priority, case-insensitive search and pagination
- `/tasks/stats` endpoint with counts per status and overdue tasks
- Input validation: blank titles, length limits, invalid enums and past due dates return `422`
- Interactive docs at `/docs` (Swagger UI), generated from the code

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks?status=&priority=&q=&skip=&limit=` | List and filter tasks |
| `GET` | `/tasks/stats` | Counts by status and overdue tasks |
| `GET` | `/tasks/{id}` | Get one task |
| `PATCH` | `/tasks/{id}` | Update some fields |
| `DELETE` | `/tasks/{id}` | Delete a task |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs

With Docker:

```bash
docker build -t task-manager-api .
docker run -p 8000:8000 task-manager-api
```

## Tests

```bash
pytest
```

Each test runs against its own in-memory SQLite database (`tests/conftest.py`), so tests are isolated and can run in any order. The suite covers happy paths, validation errors (parametrized), 404s, filters, pagination and the stats logic.

## Project structure

```
app/
  main.py       # routes and HTTP concerns (status codes, 404s)
  crud.py       # database queries, no HTTP code here
  schemas.py    # request/response models and validation rules
  models.py     # SQLAlchemy table definition
  database.py   # engine, session and the get_db dependency
tests/          # pytest suite
```

## CI

GitHub Actions runs the tests with coverage, then builds the Docker image, starts the container and checks `/health`.

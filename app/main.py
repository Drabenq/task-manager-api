from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from . import crud
from .database import Base, engine, get_db
from .models import Priority, Status
from .schemas import TaskCreate, TaskOut, TaskStats, TaskUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="REST API to manage tasks, built with FastAPI and SQLAlchemy.",
    lifespan=lifespan,
)


def _get_or_404(db: Session, task_id: int):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, data)


@app.get("/tasks", response_model=list[TaskOut], tags=["tasks"])
def list_tasks(
    status_: Status | None = Query(default=None, alias="status"),
    priority: Priority | None = None,
    q: str | None = Query(default=None, max_length=100, description="Search in title and description"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.list_tasks(db, status=status_, priority=priority, q=q, skip=skip, limit=limit)


# Declared before /tasks/{task_id} so "stats" is not parsed as an id.
@app.get("/tasks/stats", response_model=TaskStats, tags=["tasks"])
def stats(db: Session = Depends(get_db)):
    return crud.task_stats(db)


@app.get("/tasks/{task_id}", response_model=TaskOut, tags=["tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, task_id)


@app.patch("/tasks/{task_id}", response_model=TaskOut, tags=["tasks"])
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    return crud.update_task(db, task, data)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    crud.delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

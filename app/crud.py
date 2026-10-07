from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .models import Priority, Status, Task
from .schemas import TaskCreate, TaskUpdate


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def list_tasks(
    db: Session,
    status: Status | None = None,
    priority: Priority | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Task]:
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(func.lower(Task.title).like(pattern), func.lower(Task.description).like(pattern))
        )
    stmt = stmt.order_by(Task.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def task_stats(db: Session) -> dict:
    counts = dict(db.execute(select(Task.status, func.count()).group_by(Task.status)).all())
    overdue = db.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.due_date < date.today(), Task.status != Status.done)
    )
    return {
        "total": sum(counts.values()),
        "todo": counts.get(Status.todo, 0),
        "in_progress": counts.get(Status.in_progress, 0),
        "done": counts.get(Status.done, 0),
        "overdue": overdue or 0,
    }

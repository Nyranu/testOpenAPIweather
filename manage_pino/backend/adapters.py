from __future__ import annotations

from datetime import UTC, date, datetime

from .models import Task, TaskPriority, TaskStatus


def _parse_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    if hasattr(value, "toString"):
        value = value.toString("yyyy-MM-dd")
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass
    return None


def task_to_frontend_tuple(task: Task) -> tuple[str, str, str, str]:
    return (task.title, task.description, task.status, task.due_date.isoformat() if task.due_date else "")


def frontend_tuple_to_task(data: tuple) -> Task:
    title, description, status, due = data
    now = datetime.now(UTC)
    return Task(id=0, title=title, description=description, status=status or TaskStatus.NOT_STARTED.value, due_date=_parse_date(due), created_at=now, updated_at=now, priority=TaskPriority.MEDIUM.value)


def tasks_to_frontend_tuples(tasks: list[Task]) -> list[tuple]:
    return [task_to_frontend_tuple(t) for t in tasks]


def format_task_for_display(task: Task) -> str:
    icon = {TaskStatus.COMPLETED.value: "🟢", TaskStatus.IN_PROGRESS.value: "🟡", TaskStatus.NOT_STARTED.value: "🔴"}.get(task.status, "⚪")
    due = task.due_date.strftime('%d.%m.%Y') if task.due_date else "без срока"
    return f"{icon} {task.title} - {task.status} (до: {due})"

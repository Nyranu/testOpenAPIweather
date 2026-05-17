"""
Файл adapters.py.

Здесь находятся функции-переходники между backend-моделью Task
и текущим форматом фронтенда на кортежах
(title, Description, Status, DueDate).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from .models import Task, TaskPriority, TaskStatus


def _parseDate(value: Any) -> date | None:
    """Преобразует входное значение в date или None."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
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


def taskToFrontendTuple(task: Task) -> tuple[str, str, str, str]:
    """Преобразует backend-задачу в формат кортежа фронтенда."""
    due = task.DueDate.isoformat() if task.DueDate else ""
    return (task.Title, task.Description, task.Status, due)


def frontendTupleToTask(data: tuple) -> Task:
    """Создаёт временный объект Task из кортежа фронтенда."""
    Title, Description, Status, due = data
    now = datetime.now(UTC)
    return Task(
        id=0,
        Title=title,
        Description=description,
        Status=status or TaskStatus.NOT_STARTED.value,
        DueDate=_parseDate(due),
        CreatedAt=now,
        UpdatedAt=now,
        Priority=TaskPriority.MEDIUM.value,
    )


def tasksToFrontendTuples(tasks: list[Task]) -> list[tuple[str, str, str, str]]:
    """Преобразует список backend-задач в кортежи фронтенда."""
    return [taskToFrontendTuple(task) for task in tasks]


def formatTaskForDisplay(task: Task) -> str:
    """Форматирует задачу в короткую строку для отображения в списке."""
    icon = {
        TaskStatus.COMPLETED.value: "🟢",
        TaskStatus.IN_PROGRESS.value: "🟡",
        TaskStatus.NOT_STARTED.value: "🔴",
    }.get(task.Status, "⚪")
    due = task.DueDate.strftime("%d.%m.%Y") if task.DueDate else "без срока"
    return f"{icon} {task.Title} - {task.Status} (до: {due})"

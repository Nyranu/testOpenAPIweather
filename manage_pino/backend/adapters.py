"""
Файл adapters.py.

Здесь находятся функции-переходники между backend-моделью Task
и текущим форматом фронтенда на кортежах
(Title, Description, Status, DueDate).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from .models import Task, TaskPriority, TaskStatus


def _parseDate(Value: Any) -> date | None:
    """Преобразует входное значение в date или None."""
    if Value in (None, ""):
        return None
    if isinstance(Value, datetime):
        return Value.date()
    if isinstance(Value, date):
        return Value
    if hasattr(Value, "toString"):
        Value = Value.toString("yyyy-MM-dd")
    if isinstance(Value, str):
        for Format in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(Value, Format).date()
            except ValueError:
                pass
    return None


def taskToFrontendTuple(TaskItem: Task) -> tuple[str, str, str, str]:
    """Преобразует backend-задачу в формат кортежа фронтенда."""
    Due = TaskItem.DueDate.isoformat() if TaskItem.DueDate else ""
    return (TaskItem.Title, TaskItem.Description, TaskItem.Status, Due)


def frontendTupleToTask(Data: tuple) -> Task:
    """Создаёт временный объект Task из кортежа фронтенда."""
    Title, Description, Status, Due = Data
    Now = datetime.now(UTC)
    return Task(
        Id=0,
        Title=Title,
        Description=Description,
        Status=Status or TaskStatus.NOT_STARTED.value,
        DueDate=_parseDate(Due),
        CreatedAt=Now,
        UpdatedAt=Now,
        Priority=TaskPriority.MEDIUM.value,
    )


def tasksToFrontendTuples(Tasks: list[Task]) -> list[tuple[str, str, str, str]]:
    """Преобразует список backend-задач в кортежи фронтенда."""
    return [taskToFrontendTuple(TaskItem) for TaskItem in Tasks]


def formatTaskForDisplay(TaskItem: Task) -> str:
    """Форматирует задачу в короткую строку для отображения в списке."""
    Icon = {
        TaskStatus.COMPLETED.value: "🟢",
        TaskStatus.IN_PROGRESS.value: "🟡",
        TaskStatus.NOT_STARTED.value: "🔴",
    }.get(TaskItem.Status, "⚪")
    Due = TaskItem.DueDate.strftime("%d.%m.%Y") if TaskItem.DueDate else "без срока"
    return f"{Icon} {TaskItem.Title} - {TaskItem.Status} (до: {Due})"

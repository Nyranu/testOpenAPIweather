from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Optional


class TaskStatus(StrEnum):
    """Допустимые статусы задачи."""

    NOT_STARTED = "Не начата"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершена"


class TaskPriority(StrEnum):
    """Допустимые уровни приоритета задачи."""

    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


@dataclass(slots=True)
class Task:
    """Основная модель задачи для backend-ядра."""

    id: int
    title: str
    description: str = ""
    status: str = TaskStatus.NOT_STARTED.value
    due_date: Optional[date] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    priority: str = TaskPriority.MEDIUM.value
    estimated_minutes: Optional[int] = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TaskCreate:
    """Входные данные для создания задачи."""

    title: str
    description: str = ""
    status: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TaskUpdate:
    """Входные данные для частичного обновления задачи."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    tags: Optional[list[str]] = None
    clear_due_date: bool = False
    clear_estimated_minutes: bool = False


@dataclass(slots=True)
class HistoryRecord:
    """Запись об операции над задачей."""

    id: int
    created_at: datetime
    action: str
    task_id: Optional[int] = None
    task_title: Optional[str] = None
    details: Optional[str] = None

from __future__ import annotations

from typing import Protocol

from .models import HistoryRecord, Task


class TaskRepository(Protocol):
    """Контракт хранилища задач."""

    def create(self, task: Task) -> Task: ...
    def get(self, task_id: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, task_id: int, task: Task) -> Task: ...
    def delete(self, task_id: int) -> bool: ...
    def clear(self) -> None: ...


class InMemoryTaskRepository:
    """In-memory реализация хранилища задач через словарь."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        """Сохраняет задачу."""
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        """Возвращает задачу по id."""
        return self._tasks.get(task_id)

    def list(self) -> list[Task]:
        """Возвращает список всех задач."""
        return list(self._tasks.values())

    def update(self, task_id: int, task: Task) -> Task:
        """Обновляет задачу по id."""
        self._tasks[task_id] = task
        return task

    def delete(self, task_id: int) -> bool:
        """Удаляет задачу по id."""
        return self._tasks.pop(task_id, None) is not None

    def clear(self) -> None:
        """Очищает хранилище задач."""
        self._tasks.clear()


class HistoryRepository(Protocol):
    """Контракт хранилища истории действий."""

    def add(self, record: HistoryRecord) -> HistoryRecord: ...
    def list(self, limit: int | None = None) -> list[HistoryRecord]: ...
    def clear(self) -> None: ...


class InMemoryHistoryRepository:
    """In-memory реализация истории действий."""

    def __init__(self) -> None:
        self._records: list[HistoryRecord] = []

    def add(self, record: HistoryRecord) -> HistoryRecord:
        """Добавляет запись в историю."""
        self._records.append(record)
        return record

    def list(self, limit: int | None = None) -> list[HistoryRecord]:
        """Возвращает историю в обратном хронологическом порядке."""
        records = list(reversed(self._records))
        return records if limit is None else records[:limit]

    def clear(self) -> None:
        """Очищает историю."""
        self._records.clear()

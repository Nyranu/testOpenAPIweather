from __future__ import annotations

from typing import Protocol

from .models import HistoryRecord, Task


class TaskRepository(Protocol):
    def create(self, task: Task) -> Task: ...
    def get(self, task_id: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, task_id: int, task: Task) -> Task: ...
    def delete(self, task_id: int) -> bool: ...
    def clear(self) -> None: ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def update(self, task_id: int, task: Task) -> Task:
        self._tasks[task_id] = task
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def clear(self) -> None:
        self._tasks.clear()


class HistoryRepository(Protocol):
    def add(self, record: HistoryRecord) -> HistoryRecord: ...
    def list(self, limit: int | None = None) -> list[HistoryRecord]: ...
    def clear(self) -> None: ...


class InMemoryHistoryRepository:
    def __init__(self) -> None:
        self._records: list[HistoryRecord] = []

    def add(self, record: HistoryRecord) -> HistoryRecord:
        self._records.append(record)
        return record

    def list(self, limit: int | None = None) -> list[HistoryRecord]:
        records = list(reversed(self._records))
        return records if limit is None else records[:limit]

    def clear(self) -> None:
        self._records.clear()

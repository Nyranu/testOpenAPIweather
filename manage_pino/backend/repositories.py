"""Хранилища задач и истории."""
from __future__ import annotations
from typing import Protocol
from .models import HistoryRecord, Task


class TaskRepo(Protocol):
    def create(self, TaskItem: Task) -> Task: ...
    def get(self, TaskId: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, TaskId: int, TaskItem: Task) -> Task: ...
    def delete(self, TaskId: int) -> bool: ...
    def clear(self) -> None: ...


class InMemoryTaskRepo:
    def __init__(self) -> None:
        self._Tasks: dict[int, Task] = {}

    def create(self, TaskItem: Task) -> Task:
        self._Tasks[TaskItem.Id] = TaskItem
        return TaskItem

    def get(self, TaskId: int) -> Task | None:
        return self._Tasks.get(TaskId)

    def list(self) -> list[Task]:
        return list(self._Tasks.values())

    def update(self, TaskId: int, TaskItem: Task) -> Task:
        self._Tasks[TaskId] = TaskItem
        return TaskItem

    def delete(self, TaskId: int) -> bool:
        return self._Tasks.pop(TaskId, None) is not None

    def clear(self) -> None:
        self._Tasks.clear()


class HistoryRepo(Protocol):
    def add(self, Record: HistoryRecord) -> HistoryRecord: ...
    def list(self, Limit: int | None = None) -> list[HistoryRecord]: ...
    def clear(self) -> None: ...


class InMemoryHistoryRepo:
    def __init__(self) -> None:
        self._Records: list[HistoryRecord] = []

    def add(self, Record: HistoryRecord) -> HistoryRecord:
        self._Records.append(Record)
        return Record

    def list(self, Limit: int | None = None) -> list[HistoryRecord]:
        Records = list(reversed(self._Records))
        return Records if Limit is None else Records[:Limit]

    def clear(self) -> None:
        self._Records.clear()

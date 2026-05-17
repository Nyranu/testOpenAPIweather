"""
Файл repositories.py.

Здесь описан слой хранения данных и его контракты.

Сейчас используется in-memory реализация. В будущем её можно заменить
на SQLite/PostgreSQL без переписывания сервисной логики.
"""

from __future__ import annotations

from typing import Protocol

from .models import HistoryRecord, Task


class TaskRepo(Protocol):
    """
    Контракт хранилища задач.

    Сервисы работают через этот интерфейс и не зависят
    от конкретной технологии хранения.
    """

    def create(self, task: Task) -> Task: ...
    def get(self, TaskId: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, TaskId: int, task: Task) -> Task: ...
    def delete(self, TaskId: int) -> bool: ...
    def clear(self) -> None: ...


class InMemoryTaskRepo:
    """
    Простейшее хранилище задач в памяти процесса.

    Подходит для тестов и локального запуска без базы данных.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        """Сохраняет задачу и возвращает её обратно."""
        self._tasks[task.Id] = task
        return task

    def get(self, TaskId: int) -> Task | None:
        """Ищет задачу по id. Возвращает None, если задача не найдена."""
        return self._tasks.get(TaskId)

    def list(self) -> list[Task]:
        """Возвращает все задачи из памяти в виде списка."""
        return list(self._tasks.values())

    def update(self, TaskId: int, task: Task) -> Task:
        """Перезаписывает задачу по id и возвращает обновлённый объект."""
        self._tasks[TaskId] = task
        return task

    def delete(self, TaskId: int) -> bool:
        """Удаляет задачу по id. Возвращает True, если запись была."""
        return self._tasks.pop(TaskId, None) is not None

    def clear(self) -> None:
        """Полностью очищает in-memory хранилище задач."""
        self._tasks.clear()


class HistoryRepo(Protocol):
    """
    Контракт хранилища истории действий.

    Позволяет хранить журнал операций отдельно от задач.
    """

    def add(self, record: HistoryRecord) -> HistoryRecord: ...
    def list(self, limit: int | None = None) -> list[HistoryRecord]: ...
    def clear(self) -> None: ...


class InMemoryHistoryRepo:
    """
    In-memory хранилище истории действий.

    Записи хранятся в обычном списке в порядке добавления.
    """

    def __init__(self) -> None:
        self._records: list[HistoryRecord] = []

    def add(self, record: HistoryRecord) -> HistoryRecord:
        """Добавляет запись в журнал и возвращает её."""
        self._records.append(record)
        return record

    def list(self, limit: int | None = None) -> list[HistoryRecord]:
        """Возвращает историю в обратном порядке, при необходимости с limit."""
        records = list(reversed(self._records))
        return records if limit is None else records[:limit]

    def clear(self) -> None:
        """Удаляет все записи из истории."""
        self._records.clear()

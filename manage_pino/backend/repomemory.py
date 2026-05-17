"""
ПАМЯТЬ бекенда сейчас через in memory работает
"""

from __future__ import annotations
from typing import Protocol
from .models import HistoryRecord, Task

#интерфейс для работы с задачами - НЕ ЗАВИСИТ ОТ ТЕХНОЛОГИЙ ХРАНЕНИЯ т.е. встраивай хоть sql.
class TaskRepo(Protocol):
    def create(self, TaskItem: Task) -> Task: ...
    def get(self, TaskId: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, TaskId: int, TaskItem: Task) -> Task: ...
    def delete(self, TaskId: int) -> bool: ...
    def clear(self) -> None: ...

# Базовое хранилище задач в памяти процессора нуу оно подходит как временная штука
class InMemoryTaskRepo:
    def __init__(self) -> None:
        self._Tasks: dict[int, Task] = {}

    #Сохраняет и возвращает задачи
    def create(self, TaskItem: Task) -> Task:
        self._Tasks[TaskItem.Id] = TaskItem
        return TaskItem

    #Ищет задачу по id
    def get(self, TaskId: int) -> Task | None:
        return self._Tasks.get(TaskId)

    # Ищет ВСЕ задачи, но в виде списка возврат
    def list(self) -> list[Task]:
        return list(self._Tasks.values())

    # Обновляет задачу по id и возвращает уже обьект
    def update(self, TaskId: int, TaskItem: Task) -> Task:
        self._Tasks[TaskId] = TaskItem
        return TaskItem

    # Удаление задачи
    def delete(self, TaskId: int) -> bool:
        return self._Tasks.pop(TaskId, None) is not None

    """ПОЛНАЯ ОЧИСТКА ХРАНИЛИЩА ЗАДАЧ!!!!!! """
    def clear(self) -> None:
        self._Tasks.clear()

# Может хранить журнал операций - при этом отдельно от задач
class HistoryRepo(Protocol):
    def add(self, Record: HistoryRecord) -> HistoryRecord: ...
    def list(self, Limit: int | None = None) -> list[HistoryRecord]: ...
    def clear(self) -> None: ...

# Хранилище истории действий пользователя - запись в обычный список в порядке добавлениия
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
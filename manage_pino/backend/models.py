"""
Файл models.py.

Здесь описаны структуры данных backend-ядра: модели задач,
данные для создания/обновления, статусы, приоритеты и история действий.

Файл не содержит бизнес-логику и не работает с хранилищем.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Optional


class TaskStatus(StrEnum):
    """
    Статусы жизненного цикла задачи.

    Используются сервисами и фронтендом для единых значений.
    """

    NOT_STARTED = "Не начата"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершена"


class TaskPriority(StrEnum):
    """
    Уровни приоритета задачи.

    Нужны для сортировки, фильтрации и планирования.
    """

    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"


@dataclass(slots=True)
class Task:
    """Основная модель одной задачи в backend-ядре."""

    Id: int  # Уникальный идентификатор задачи внутри backend.
    Title: str  # Короткое название задачи.
    Description: str = ""  # Подробное описание задачи.
    Status: str = TaskStatus.NOT_STARTED.value  # Текущий статус выполнения.
    DueDate: Optional[date] = None  # Дедлайн, если задан.
    CreatedAt: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата создания.
    UpdatedAt: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата последнего изменения.
    CompletedAt: Optional[datetime] = None  # Когда задача завершена.
    Priority: str = TaskPriority.MEDIUM.value  # Приоритет задачи.
    EstimatedMinutes: Optional[int] = None  # Оценка длительности в минутах.
    Tags: list[str] = field(default_factory=list)  # Текстовые метки для группировки.


@dataclass(slots=True)
class TaskCreate:
    """Входные данные для создания новой задачи."""

    Title: str  # Название новой задачи.
    Description: str = ""  # Описание новой задачи.
    Status: Optional[str] = None  # Опциональный начальный статус.
    DueDate: Optional[date] = None  # Опциональный дедлайн.
    Priority: Optional[str] = None  # Опциональный приоритет.
    EstimatedMinutes: Optional[int] = None  # Опциональная оценка времени.
    Tags: list[str] = field(default_factory=list)  # Опциональные метки.


@dataclass(slots=True)
class TaskUpdate:
    """Данные для частичного обновления существующей задачи."""

    Title: Optional[str] = None  # Новое название.
    Description: Optional[str] = None  # Новое описание.
    Status: Optional[str] = None  # Новый статус.
    DueDate: Optional[date] = None  # Новый дедлайн.
    Priority: Optional[str] = None  # Новый приоритет.
    EstimatedMinutes: Optional[int] = None  # Новая оценка в минутах.
    Tags: Optional[list[str]] = None  # Новый набор меток.
    ClearDueDate: bool = False  # Явно очистить дедлайн.
    ClearEstimatedMinutes: bool = False  # Явно очистить оценку времени.


@dataclass(slots=True)
class HistoryRecord:
    """Запись об одном действии пользователя над задачами."""

    Id: int  # Уникальный id записи истории.
    CreatedAt: datetime  # Время создания записи.
    Action: str  # Имя действия (createTask, updateTask и т.д.).
    TaskId: Optional[int] = None  # id связанной задачи.
    TaskTitle: Optional[str] = None  # Заголовок связанной задачи.
    Details: Optional[str] = None  # Дополнительное пояснение действия.

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

    id: int  # Уникальный идентификатор задачи внутри backend.
    title: str  # Короткое название задачи.
    description: str = ""  # Подробное описание задачи.
    status: str = TaskStatus.NOT_STARTED.value  # Текущий статус выполнения.
    due_date: Optional[date] = None  # Дедлайн, если задан.
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата создания.
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата последнего изменения.
    completed_at: Optional[datetime] = None  # Когда задача завершена.
    priority: str = TaskPriority.MEDIUM.value  # Приоритет задачи.
    estimated_minutes: Optional[int] = None  # Оценка длительности в минутах.
    tags: list[str] = field(default_factory=list)  # Текстовые метки для группировки.


@dataclass(slots=True)
class TaskCreate:
    """Входные данные для создания новой задачи."""

    title: str  # Название новой задачи.
    description: str = ""  # Описание новой задачи.
    status: Optional[str] = None  # Опциональный начальный статус.
    due_date: Optional[date] = None  # Опциональный дедлайн.
    priority: Optional[str] = None  # Опциональный приоритет.
    estimated_minutes: Optional[int] = None  # Опциональная оценка времени.
    tags: list[str] = field(default_factory=list)  # Опциональные метки.


@dataclass(slots=True)
class TaskUpdate:
    """Данные для частичного обновления существующей задачи."""

    title: Optional[str] = None  # Новое название.
    description: Optional[str] = None  # Новое описание.
    status: Optional[str] = None  # Новый статус.
    due_date: Optional[date] = None  # Новый дедлайн.
    priority: Optional[str] = None  # Новый приоритет.
    estimated_minutes: Optional[int] = None  # Новая оценка в минутах.
    tags: Optional[list[str]] = None  # Новый набор меток.
    clear_due_date: bool = False  # Явно очистить дедлайн.
    clear_estimated_minutes: bool = False  # Явно очистить оценку времени.


@dataclass(slots=True)
class HistoryRecord:
    """Запись об одном действии пользователя над задачами."""

    id: int  # Уникальный id записи истории.
    created_at: datetime  # Время создания записи.
    action: str  # Имя действия (create_task, update_task и т.д.).
    task_id: Optional[int] = None  # id связанной задачи.
    task_title: Optional[str] = None  # Заголовок связанной задачи.
    details: Optional[str] = None  # Дополнительное пояснение действия.

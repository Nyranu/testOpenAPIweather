"""
Основные модели данных как и что содержат, можешь некоторые пункты дополнить, но нужно будет по аналогии также
дополнить и в остальных где они используются но там все просто - просто копируй как там где они используются

Там где в переменной Optional - означает что значение опциональное и не обязательное
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Optional

# Статусы
class TaskStatus(StrEnum):
    NOT_STARTED = "Не начата"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершена"

# Приоритет
class TaskPriority(StrEnum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"

# Основная МОДЕЛЬ ЗАДАЧИ - то что и с чем ты работаешь на стороне бекенда трындец какая важная штука - ее не трогать
@dataclass(slots=True)
class Task:
    Id: int
    Title: str
    Description: str = ""
    Status: str = TaskStatus.NOT_STARTED.value
    DueDate: Optional[date] = None  # Дедлайн
    CreatedAt: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата создания
    UpdatedAt: datetime = field(default_factory=lambda: datetime.now(UTC))  # Дата последнего изменения
    CompletedAt: Optional[datetime] = None  # Когда задача завершена
    Priority: str = TaskPriority.MEDIUM.value
    EstimatedMinutes: Optional[int] = None  # Оценка длительности в минутах
    Tags: list[str] = field(default_factory=list)  # Теги для группировки

# Его ты будешь постоянно использовать - модель для создания задачи - входные данные
@dataclass(slots=True)
class TaskCreate:
    Title: str  #Название новой задачи
    Description: str = ""  #Описание новой задачи
    Status: Optional[str] = None  #Начальный статус
    DueDate: Optional[date] = None  #Ддедлайн
    Priority: Optional[str] = None  #Приоритет
    EstimatedMinutes: Optional[int] = None  #Оценка времени
    Tags: list[str] = field(default_factory=list)  # Теги

# Модель для обновления данных
@dataclass(slots=True)
class TaskUpdate:
    Title: Optional[str] = None
    Description: Optional[str] = None
    Status: Optional[str] = None
    DueDate: Optional[date] = None
    Priority: Optional[str] = None
    EstimatedMinutes: Optional[int] = None
    Tags: Optional[list[str]] = None
    ClearDueDate: bool = False  # Явно очистить дедлайна
    ClearEstimatedMinutes: bool = False  # Явная очистка времени

#Запись об одном действии который совершилл пользователь над задачей - модель для логов/истории
@dataclass(slots=True)
class HistoryRecord:
    Id: int
    CreatedAt: datetime
    Action: str  # Действие
    TaskId: Optional[int] = None
    TaskTitle: Optional[str] = None
    Details: Optional[str] = None  # Доп обьяснения

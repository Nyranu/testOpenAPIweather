"""
Меняет твои картежи из фронтенда на Task модуль бекенда и обратно - основной функционал тут через модель Task

"""

from __future__ import annotations
from datetime import UTC, date, datetime
from typing import Any
from .models import Task, TaskPriority, TaskStatus

# Преобразует значение в формате даты в именно тип(формат) даты)
def _parseDate(Value: Any) -> date | None:
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

# Преобразует таск в твой кортеж для фронтенда!!!
def taskToFrontendTuple(TaskItem: Task) -> tuple[str, str, str, str]:
    Due = TaskItem.DueDate.isoformat() if TaskItem.DueDate else ""
    return (TaskItem.Title, TaskItem.Description, TaskItem.Status, Due)

# Такси из бекенда в список кортежей для фронтенда
def tasksToFrontendTuples(Tasks: list[Task]) -> list[tuple[str, str, str, str]]:
    return [taskToFrontendTuple(TaskItem) for TaskItem in Tasks]

# ЭТО ВРЕМЕННЫЙ ОБЬЕКТ TASK - можешь его как пример-заготовку, или для тестов, НО НЕ НА ПОСТОЯНКУ
def frontendTupleToTask(Data: tuple) -> Task:
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




#Я увидел прикалюху в плане иконок статусов - сюда можешь вставить какие нибудь иконки для отображения задач - он выводит как раз
#иконку - название - стаус и дедлайн. Вместо + +- - ~~ просто вставь хоть эмодзи хоть что Завершенный - в процессе - не начат - базовый статус
def formatTaskForDisplay(TaskItem: Task) -> str:
    Icon = {
        TaskStatus.COMPLETED.value: "+",
        TaskStatus.IN_PROGRESS.value: "~~",
        TaskStatus.NOT_STARTED.value: "-",
    }.get(TaskItem.Status, "+-")
    Due = TaskItem.DueDate.strftime("%d.%m.%Y") if TaskItem.DueDate else "без срока"
    return f"{Icon} {TaskItem.Title} - {TaskItem.Status} (до: {Due})"

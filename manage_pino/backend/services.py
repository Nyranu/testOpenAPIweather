"""
Файл services.py.

Здесь находится основная бизнес-логика менеджера задач:
создание, обновление, удаление, фильтрация и история действий.

Фронтенд должен вызывать эти классы, а не работать с хранилищами напрямую.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from .exceptions import InvalidPriorityError, InvalidStatusError, TaskNotFoundError, ValidationError
from .models import HistoryRecord, Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from .repositories import HistoryRepo, TaskRepo


class History:
    """Класс для добавления, чтения и очистки истории действий."""

    def __init__(self, Repo: HistoryRepo) -> None:
        self.Repo = Repo
        self._nextId = 1

    def addHistory(self, Action: str, TaskId: int | None = None, TaskTitle: str | None = None, Details: str | None = None) -> HistoryRecord:
        Record = HistoryRecord(self._nextId, datetime.now(UTC), Action, TaskId, TaskTitle, Details)
        self._nextId += 1
        return self.Repo.add(Record)

    def listHistory(self, Limit: int = 50) -> list[HistoryRecord]:
        return self.Repo.list(limit=Limit)

    def clearHistory(self) -> None:
        self.Repo.clear()


class TaskManager:
    """Главный класс управления задачами и проверками данных."""

    def __init__(self, TaskRepoObj: TaskRepo, HistoryObj: History) -> None:
        self.TaskRepoObj = TaskRepoObj
        self.HistoryObj = HistoryObj
        self._nextId = 1

    def _validateStatus(self, Status: str) -> None:
        if Status not in [s.value for s in TaskStatus]:
            raise InvalidStatusError(Status)

    def _validatePriority(self, Priority: str) -> None:
        if Priority not in [p.value for p in TaskPriority]:
            raise InvalidPriorityError(Priority)

    def _validateEstimatedMinutes(self, EstimatedMinutes: int | None) -> None:
        if EstimatedMinutes is not None and EstimatedMinutes <= 0:
            raise ValidationError("EstimatedMinutes must be greater than 0")

    def createTask(self, Data: TaskCreate) -> Task:
        if not Data.Title or not Data.Title.strip():
            raise ValidationError("Task Title cannot be empty")
        Status = Data.Status or TaskStatus.NOT_STARTED.value
        Priority = Data.Priority or TaskPriority.MEDIUM.value
        self._validateStatus(Status)
        self._validatePriority(Priority)
        self._validateEstimatedMinutes(Data.EstimatedMinutes)

        Now = datetime.now(UTC)
        CompletedAt = Now if Status == TaskStatus.COMPLETED.value else None
        TaskItem = Task(
            Id=self._nextId,
            Title=Data.Title.strip(),
            Description=Data.Description,
            Status=Status,
            DueDate=Data.DueDate,
            CreatedAt=Now,
            UpdatedAt=Now,
            CompletedAt=CompletedAt,
            Priority=Priority,
            EstimatedMinutes=Data.EstimatedMinutes,
            Tags=list(Data.Tags),
        )
        self._nextId += 1
        self.TaskRepoObj.create(TaskItem)
        self.HistoryObj.addHistory("createTask", TaskItem.Id, TaskItem.Title, f"Создана задача со статусом {TaskItem.Status}")
        return TaskItem

    def getTask(self, TaskId: int) -> Task:
        TaskItem = self.TaskRepoObj.get(TaskId)
        if not TaskItem:
            raise TaskNotFoundError(f"Task {TaskId} not found")
        return TaskItem

    def listTasks(self, Status: str | None = None, Priority: str | None = None, OverdueOnly: bool = False, Search: str | None = None) -> list[Task]:
        TaskList = self.TaskRepoObj.list()
        if Status:
            self._validateStatus(Status)
            TaskList = [t for t in TaskList if t.Status == Status]
        if Priority:
            self._validatePriority(Priority)
            TaskList = [t for t in TaskList if t.Priority == Priority]
        if OverdueOnly:
            Today = date.today()
            TaskList = [t for t in TaskList if t.DueDate and t.DueDate < Today and t.Status != TaskStatus.COMPLETED.value]
        if Search:
            Query = Search.lower().strip()
            TaskList = [t for t in TaskList if Query in t.Title.lower() or Query in t.Description.lower()]
        return TaskList

    def updateTask(self, TaskId: int, Data: TaskUpdate) -> Task:
        OldTask = self.getTask(TaskId)
        NewTask = replace(OldTask)

        if Data.Title is not None:
            NewTask.Title = Data.Title.strip()
        if Data.Description is not None:
            NewTask.Description = Data.Description
        if Data.DueDate is not None:
            NewTask.DueDate = Data.DueDate
        if Data.EstimatedMinutes is not None:
            NewTask.EstimatedMinutes = Data.EstimatedMinutes
        if Data.ClearDueDate:
            NewTask.DueDate = None
        if Data.ClearEstimatedMinutes:
            NewTask.EstimatedMinutes = None
        if Data.Tags is not None:
            NewTask.Tags = list(Data.Tags)
        if Data.Status is not None:
            self._validateStatus(Data.Status)
            NewTask.Status = Data.Status
        if Data.Priority is not None:
            self._validatePriority(Data.Priority)
            NewTask.Priority = Data.Priority

        if not NewTask.Title.strip():
            raise ValidationError("Task Title cannot be empty")
        self._validateEstimatedMinutes(NewTask.EstimatedMinutes)

        if NewTask.Status == TaskStatus.COMPLETED.value and OldTask.Status != TaskStatus.COMPLETED.value:
            NewTask.CompletedAt = datetime.now(UTC)
        elif OldTask.Status == TaskStatus.COMPLETED.value and NewTask.Status != TaskStatus.COMPLETED.value:
            NewTask.CompletedAt = None

        NewTask.UpdatedAt = datetime.now(UTC)
        self.TaskRepoObj.update(TaskId, NewTask)
        self.HistoryObj.addHistory("updateTask", NewTask.Id, NewTask.Title, "Обновлены поля задачи")
        return NewTask

    def deleteTask(self, TaskId: int) -> bool:
        TaskItem = self.getTask(TaskId)
        Deleted = self.TaskRepoObj.delete(TaskId)
        self.HistoryObj.addHistory("deleteTask", TaskItem.Id, TaskItem.Title, "Задача удалена")
        return Deleted

    def changeStatus(self, TaskId: int, Status: str) -> Task:
        return self.updateTask(TaskId, TaskUpdate(Status=Status))

    def completeTask(self, TaskId: int) -> Task:
        return self.changeStatus(TaskId, TaskStatus.COMPLETED.value)

    def reopenTask(self, TaskId: int) -> Task:
        return self.changeStatus(TaskId, TaskStatus.IN_PROGRESS.value)

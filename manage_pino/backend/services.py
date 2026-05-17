from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from .exceptions import InvalidPriorityError, InvalidStatusError, TaskNotFoundError, ValidationError
from .models import HistoryRecord, Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from .repositories import HistoryRepository, TaskRepository


class HistoryService:
    def __init__(self, repository: HistoryRepository) -> None:
        self.repository = repository
        self._next_id = 1

    def add_history(self, action: str, task_id: int | None = None, task_title: str | None = None, details: str | None = None) -> HistoryRecord:
        rec = HistoryRecord(self._next_id, datetime.now(UTC), action, task_id, task_title, details)
        self._next_id += 1
        return self.repository.add(rec)

    def list_history(self, limit: int = 50) -> list[HistoryRecord]:
        return self.repository.list(limit=limit)

    def clear_history(self) -> None:
        self.repository.clear()


class TaskService:
    def __init__(self, task_repository: TaskRepository, history_service: HistoryService) -> None:
        self.task_repository = task_repository
        self.history_service = history_service
        self._next_id = 1

    def _validate_status(self, status: str) -> None:
        if status not in [s.value for s in TaskStatus]:
            raise InvalidStatusError(status)

    def _validate_priority(self, priority: str) -> None:
        if priority not in [p.value for p in TaskPriority]:
            raise InvalidPriorityError(priority)

    def create_task(self, data: TaskCreate) -> Task:
        if not data.title or not data.title.strip():
            raise ValidationError("Task title cannot be empty")
        status = data.status or TaskStatus.NOT_STARTED.value
        priority = data.priority or TaskPriority.MEDIUM.value
        self._validate_status(status)
        self._validate_priority(priority)
        now = datetime.now(UTC)
        task = Task(id=self._next_id, title=data.title.strip(), description=data.description, status=status, due_date=data.due_date,
                    created_at=now, updated_at=now, priority=priority, estimated_minutes=data.estimated_minutes, tags=data.tags)
        self._next_id += 1
        self.task_repository.create(task)
        self.history_service.add_history("create_task", task.id, task.title, f"Создана задача со статусом {task.status}")
        return task

    def get_task(self, task_id: int) -> Task:
        task = self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(self, status: str | None = None, priority: str | None = None, overdue_only: bool = False, search: str | None = None) -> list[Task]:
        tasks = self.task_repository.list()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if overdue_only:
            today = date.today()
            tasks = [t for t in tasks if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED.value]
        if search:
            q = search.lower().strip()
            tasks = [t for t in tasks if q in t.title.lower() or q in t.description.lower()]
        return tasks

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        new = replace(task)
        for field_name in ["title", "description", "due_date", "estimated_minutes"]:
            val = getattr(data, field_name)
            if val is not None:
                setattr(new, field_name, val)
        if data.tags is not None:
            new.tags = data.tags
        if data.status is not None:
            self._validate_status(data.status)
            new.status = data.status
        if data.priority is not None:
            self._validate_priority(data.priority)
            new.priority = data.priority
        if not new.title.strip():
            raise ValidationError("Task title cannot be empty")
        if new.status == TaskStatus.COMPLETED.value and task.status != TaskStatus.COMPLETED.value:
            new.completed_at = datetime.now(UTC)
        elif task.status == TaskStatus.COMPLETED.value and new.status != TaskStatus.COMPLETED.value:
            new.completed_at = None
        new.updated_at = datetime.now(UTC)
        self.task_repository.update(task_id, new)
        self.history_service.add_history("update_task", new.id, new.title, "Обновлены поля задачи")
        return new

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        deleted = self.task_repository.delete(task_id)
        self.history_service.add_history("delete_task", task.id, task.title, "Задача удалена")
        return deleted

    def change_status(self, task_id: int, status: str) -> Task:
        return self.update_task(task_id, TaskUpdate(status=status))

    def complete_task(self, task_id: int) -> Task:
        return self.change_status(task_id, TaskStatus.COMPLETED.value)

    def reopen_task(self, task_id: int) -> Task:
        return self.change_status(task_id, TaskStatus.IN_PROGRESS.value)

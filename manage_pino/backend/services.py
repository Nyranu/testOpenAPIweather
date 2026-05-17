from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from .exceptions import InvalidPriorityError, InvalidStatusError, TaskNotFoundError, ValidationError
from .models import HistoryRecord, Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from .repositories import HistoryRepository, TaskRepository


class HistoryService:
    """Сервис работы с историей действий."""

    def __init__(self, repository: HistoryRepository) -> None:
        self.repository = repository
        self._next_id = 1

    def add_history(
        self,
        action: str,
        task_id: int | None = None,
        task_title: str | None = None,
        details: str | None = None,
    ) -> HistoryRecord:
        """Добавляет запись в историю."""
        rec = HistoryRecord(self._next_id, datetime.now(UTC), action, task_id, task_title, details)
        self._next_id += 1
        return self.repository.add(rec)

    def list_history(self, limit: int = 50) -> list[HistoryRecord]:
        """Возвращает последние записи истории."""
        return self.repository.list(limit=limit)

    def clear_history(self) -> None:
        """Очищает историю действий."""
        self.repository.clear()


class TaskService:
    """Сервис бизнес-логики для задач."""

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

    def _validate_estimated_minutes(self, estimated_minutes: int | None) -> None:
        if estimated_minutes is not None and estimated_minutes <= 0:
            raise ValidationError("estimated_minutes must be greater than 0")

    def create_task(self, data: TaskCreate) -> Task:
        """Создаёт задачу, валидирует данные и пишет историю."""
        if not data.title or not data.title.strip():
            raise ValidationError("Task title cannot be empty")
        status = data.status or TaskStatus.NOT_STARTED.value
        priority = data.priority or TaskPriority.MEDIUM.value
        self._validate_status(status)
        self._validate_priority(priority)
        self._validate_estimated_minutes(data.estimated_minutes)

        now = datetime.now(UTC)
        completed_at = now if status == TaskStatus.COMPLETED.value else None
        task = Task(
            id=self._next_id,
            title=data.title.strip(),
            description=data.description,
            status=status,
            due_date=data.due_date,
            created_at=now,
            updated_at=now,
            completed_at=completed_at,
            priority=priority,
            estimated_minutes=data.estimated_minutes,
            tags=list(data.tags),
        )
        self._next_id += 1
        self.task_repository.create(task)
        self.history_service.add_history("create_task", task.id, task.title, f"Создана задача со статусом {task.status}")
        return task

    def get_task(self, task_id: int) -> Task:
        """Возвращает задачу по id или выбрасывает TaskNotFoundError."""
        task = self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(
        self,
        status: str | None = None,
        priority: str | None = None,
        overdue_only: bool = False,
        search: str | None = None,
    ) -> list[Task]:
        """Возвращает задачи с фильтрами по статусу, приоритету, просрочке и поиску."""
        tasks = self.task_repository.list()
        if status:
            self._validate_status(status)
            tasks = [t for t in tasks if t.status == status]
        if priority:
            self._validate_priority(priority)
            tasks = [t for t in tasks if t.priority == priority]
        if overdue_only:
            today = date.today()
            tasks = [t for t in tasks if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED.value]
        if search:
            q = search.lower().strip()
            tasks = [t for t in tasks if q in t.title.lower() or q in t.description.lower()]
        return tasks

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        """Обновляет задачу по id и учитывает спец-флаги очистки полей."""
        task = self.get_task(task_id)
        new = replace(task)

        if data.title is not None:
            new.title = data.title.strip()
        if data.description is not None:
            new.description = data.description
        if data.due_date is not None:
            new.due_date = data.due_date
        if data.estimated_minutes is not None:
            new.estimated_minutes = data.estimated_minutes

        if data.clear_due_date:
            new.due_date = None
        if data.clear_estimated_minutes:
            new.estimated_minutes = None

        if data.tags is not None:
            new.tags = list(data.tags)
        if data.status is not None:
            self._validate_status(data.status)
            new.status = data.status
        if data.priority is not None:
            self._validate_priority(data.priority)
            new.priority = data.priority

        if not new.title.strip():
            raise ValidationError("Task title cannot be empty")
        self._validate_estimated_minutes(new.estimated_minutes)

        if new.status == TaskStatus.COMPLETED.value and task.status != TaskStatus.COMPLETED.value:
            new.completed_at = datetime.now(UTC)
        elif task.status == TaskStatus.COMPLETED.value and new.status != TaskStatus.COMPLETED.value:
            new.completed_at = None

        new.updated_at = datetime.now(UTC)
        self.task_repository.update(task_id, new)
        self.history_service.add_history("update_task", new.id, new.title, "Обновлены поля задачи")
        return new

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по id."""
        task = self.get_task(task_id)
        deleted = self.task_repository.delete(task_id)
        self.history_service.add_history("delete_task", task.id, task.title, "Задача удалена")
        return deleted

    def change_status(self, task_id: int, status: str) -> Task:
        """Изменяет статус задачи."""
        return self.update_task(task_id, TaskUpdate(status=status))

    def complete_task(self, task_id: int) -> Task:
        """Переводит задачу в статус 'Завершена'."""
        return self.change_status(task_id, TaskStatus.COMPLETED.value)

    def reopen_task(self, task_id: int) -> Task:
        """Возвращает завершённую задачу в работу."""
        return self.change_status(task_id, TaskStatus.IN_PROGRESS.value)

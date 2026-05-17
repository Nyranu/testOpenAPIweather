from __future__ import annotations

from datetime import date, timedelta

from .models import Task, TaskPriority, TaskStatus


class TimeManagementService:
    """Сервис для выборок и планирования задач по времени."""

    def get_overdue_tasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает незавершённые задачи с истёкшим дедлайном."""
        today = date.today()
        return [t for t in tasks if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED.value]

    def get_today_tasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает незавершённые задачи на сегодня."""
        today = date.today()
        return [t for t in tasks if t.due_date == today and t.status != TaskStatus.COMPLETED.value]

    def get_upcoming_tasks(self, tasks: list[Task], days: int = 7) -> list[Task]:
        """Возвращает незавершённые задачи на ближайшие N дней."""
        today, end = date.today(), date.today() + timedelta(days=days)
        return [t for t in tasks if t.due_date and today < t.due_date <= end and t.status != TaskStatus.COMPLETED.value]

    def get_completed_tasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает завершённые задачи."""
        return [t for t in tasks if t.status == TaskStatus.COMPLETED.value]

    def get_workload_by_day(self, tasks: list[Task], days: int = 7) -> dict[str, int]:
        """Возвращает суммарную нагрузку по дням в минутах."""
        today = date.today()
        result = {str(today + timedelta(days=i)): 0 for i in range(days)}
        for task in tasks:
            if task.due_date and str(task.due_date) in result and task.status != TaskStatus.COMPLETED.value:
                result[str(task.due_date)] += task.estimated_minutes or 30
        return result

    def sort_by_deadline(self, tasks: list[Task]) -> list[Task]:
        """Сортирует задачи по дедлайну, задачи без срока — в конце."""
        return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or date.max))

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Сортирует задачи по приоритету: высокий -> средний -> низкий."""
        order = {TaskPriority.HIGH.value: 0, TaskPriority.MEDIUM.value: 1, TaskPriority.LOW.value: 2}
        return sorted(tasks, key=lambda t: order.get(t.priority, 99))

    def get_task_urgency(self, task: Task) -> str:
        """Определяет срочность задачи."""
        if task.status == TaskStatus.COMPLETED.value:
            return "completed"
        if not task.due_date:
            return "normal"
        today = date.today()
        if task.due_date < today:
            return "overdue"
        if task.due_date == today:
            return "today"
        if task.due_date <= today + timedelta(days=3):
            return "soon"
        return "normal"

    def suggest_daily_plan(self, tasks: list[Task], available_minutes: int = 240) -> list[Task]:
        """Предлагает план на день по приоритетам и доступному времени."""
        filtered = [t for t in tasks if t.status != TaskStatus.COMPLETED.value]
        overdue = self.get_overdue_tasks(filtered)
        today_tasks = [t for t in self.get_today_tasks(filtered) if t not in overdue]
        high = [
            t
            for t in self.sort_by_priority(filtered)
            if t.priority == TaskPriority.HIGH.value and t not in overdue and t not in today_tasks
        ]
        rest = [t for t in self.sort_by_deadline(filtered) if t not in overdue and t not in today_tasks and t not in high]
        ordered = overdue + today_tasks + high + rest

        plan: list[Task] = []
        used = 0
        for task in ordered:
            cost = task.estimated_minutes or 30
            if used + cost <= available_minutes:
                plan.append(task)
                used += cost
        return plan

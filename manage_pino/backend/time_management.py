"""
Файл time_management.py.

Содержит функции для планирования задач по времени:
просрочка, задачи на сегодня, ближайшие дедлайны и дневной план.
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Task, TaskPriority, TaskStatus


class TimeManagement:
    """Сервис для выборок и планирования задач по времени."""

    def getOverdueTasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает незавершённые задачи с истёкшим дедлайном."""
        today = date.today()
        return [t for t in tasks if t.DueDate and t.DueDate < today and t.Status != TaskStatus.COMPLETED.value]

    def getTodayTasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает незавершённые задачи на сегодня."""
        today = date.today()
        return [t for t in tasks if t.DueDate == today and t.Status != TaskStatus.COMPLETED.value]

    def getUpcomingTasks(self, tasks: list[Task], days: int = 7) -> list[Task]:
        """Возвращает незавершённые задачи на ближайшие N дней."""
        today, end = date.today(), date.today() + timedelta(days=days)
        return [t for t in tasks if t.DueDate and today < t.DueDate <= end and t.Status != TaskStatus.COMPLETED.value]

    def getCompletedTasks(self, tasks: list[Task]) -> list[Task]:
        """Возвращает завершённые задачи."""
        return [t for t in tasks if t.Status == TaskStatus.COMPLETED.value]

    def getWorkloadByDay(self, tasks: list[Task], days: int = 7) -> dict[str, int]:
        """Возвращает суммарную нагрузку по дням в минутах."""
        today = date.today()
        result = {str(today + timedelta(days=i)): 0 for i in range(days)}
        for task in tasks:
            if task.DueDate and str(task.DueDate) in result and task.Status != TaskStatus.COMPLETED.value:
                result[str(task.DueDate)] += task.EstimatedMinutes or 30
        return result

    def sortByDeadline(self, tasks: list[Task]) -> list[Task]:
        """Сортирует задачи по дедлайну, задачи без срока — в конце."""
        return sorted(tasks, key=lambda t: (t.DueDate is None, t.DueDate or date.max))

    def sortByPriority(self, tasks: list[Task]) -> list[Task]:
        """Сортирует задачи по приоритету: высокий -> средний -> низкий."""
        order = {TaskPriority.HIGH.value: 0, TaskPriority.MEDIUM.value: 1, TaskPriority.LOW.value: 2}
        return sorted(tasks, key=lambda t: order.get(t.Priority, 99))

    def getTask_urgency(self, task: Task) -> str:
        """Определяет срочность задачи."""
        if task.Status == TaskStatus.COMPLETED.value:
            return "completed"
        if not task.DueDate:
            return "normal"
        today = date.today()
        if task.DueDate < today:
            return "overdue"
        if task.DueDate == today:
            return "today"
        if task.DueDate <= today + timedelta(days=3):
            return "soon"
        return "normal"

    def suggestDailyPlan(self, tasks: list[Task], AvailableMinutes: int = 240) -> list[Task]:
        """Предлагает план на день по приоритетам и доступному времени."""
        filtered = [t for t in tasks if t.Status != TaskStatus.COMPLETED.value]
        overdue = self.getOverdueTasks(filtered)
        TodayTasks = [t for t in self.getTodayTasks(filtered) if t not in overdue]
        high = [
            t
            for t in self.sortByPriority(filtered)
            if t.Priority == TaskPriority.HIGH.value and t not in overdue and t not in TodayTasks
        ]
        rest = [t for t in self.sortByDeadline(filtered) if t not in overdue and t not in TodayTasks and t not in high]
        ordered = overdue + TodayTasks + high + rest

        plan: list[Task] = []
        used = 0
        for task in ordered:
            cost = task.EstimatedMinutes or 30
            if used + cost <= AvailableMinutes:
                plan.append(task)
                used += cost
        return plan

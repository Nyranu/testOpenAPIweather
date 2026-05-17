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

    def getOverdueTasks(self, Tasks: list[Task]) -> list[Task]:
        Today = date.today()
        return [TaskItem for TaskItem in Tasks if TaskItem.DueDate and TaskItem.DueDate < Today and TaskItem.Status != TaskStatus.COMPLETED.value]

    def getTodayTasks(self, Tasks: list[Task]) -> list[Task]:
        Today = date.today()
        return [TaskItem for TaskItem in Tasks if TaskItem.DueDate == Today and TaskItem.Status != TaskStatus.COMPLETED.value]

    def getUpcomingTasks(self, Tasks: list[Task], Days: int = 7) -> list[Task]:
        Today = date.today()
        End = Today + timedelta(days=Days)
        return [TaskItem for TaskItem in Tasks if TaskItem.DueDate and Today < TaskItem.DueDate <= End and TaskItem.Status != TaskStatus.COMPLETED.value]

    def getCompletedTasks(self, Tasks: list[Task]) -> list[Task]:
        return [TaskItem for TaskItem in Tasks if TaskItem.Status == TaskStatus.COMPLETED.value]

    def getWorkloadByDay(self, Tasks: list[Task], Days: int = 7) -> dict[str, int]:
        Today = date.today()
        Result = {str(Today + timedelta(days=Index)): 0 for Index in range(Days)}
        for TaskItem in Tasks:
            if TaskItem.DueDate and str(TaskItem.DueDate) in Result and TaskItem.Status != TaskStatus.COMPLETED.value:
                Result[str(TaskItem.DueDate)] += TaskItem.EstimatedMinutes or 30
        return Result

    def sortByDeadline(self, Tasks: list[Task]) -> list[Task]:
        return sorted(Tasks, key=lambda TaskItem: (TaskItem.DueDate is None, TaskItem.DueDate or date.max))

    def sortByPriority(self, Tasks: list[Task]) -> list[Task]:
        Order = {TaskPriority.HIGH.value: 0, TaskPriority.MEDIUM.value: 1, TaskPriority.LOW.value: 2}
        return sorted(Tasks, key=lambda TaskItem: Order.get(TaskItem.Priority, 99))

    def getTaskUrgency(self, TaskItem: Task) -> str:
        if TaskItem.Status == TaskStatus.COMPLETED.value:
            return "completed"
        if not TaskItem.DueDate:
            return "normal"
        Today = date.today()
        if TaskItem.DueDate < Today:
            return "overdue"
        if TaskItem.DueDate == Today:
            return "today"
        if TaskItem.DueDate <= Today + timedelta(days=3):
            return "soon"
        return "normal"

    def suggestDailyPlan(self, Tasks: list[Task], AvailableMinutes: int = 240) -> list[Task]:
        Filtered = [TaskItem for TaskItem in Tasks if TaskItem.Status != TaskStatus.COMPLETED.value]
        Overdue = self.getOverdueTasks(Filtered)
        TodayTasks = [TaskItem for TaskItem in self.getTodayTasks(Filtered) if TaskItem not in Overdue]
        High = [
            TaskItem
            for TaskItem in self.sortByPriority(Filtered)
            if TaskItem.Priority == TaskPriority.HIGH.value and TaskItem not in Overdue and TaskItem not in TodayTasks
        ]
        Rest = [TaskItem for TaskItem in self.sortByDeadline(Filtered) if TaskItem not in Overdue and TaskItem not in TodayTasks and TaskItem not in High]
        Ordered = Overdue + TodayTasks + High + Rest

        Plan: list[Task] = []
        Used = 0
        for TaskItem in Ordered:
            Cost = TaskItem.EstimatedMinutes or 30
            if Used + Cost <= AvailableMinutes:
                Plan.append(TaskItem)
                Used += Cost
        return Plan

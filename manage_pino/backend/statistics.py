"""
Файл statistics.py.

Содержит расчёты статистики по задачам:
сводка, распределения, процент завершения и дедлайн-метрики.
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Task, TaskPriority, TaskStatus


class Statistics:
    """Сервис расчёта статистики по задачам."""

    def getSummary(self, tasks: list[Task], HistoryCount: int = 0) -> dict:
        """Возвращает основную сводку по задачам и истории."""
        total = len(tasks)
        completed = sum(t.Status == TaskStatus.COMPLETED.value for t in tasks)
        inProgress = sum(t.Status == TaskStatus.IN_PROGRESS.value for t in tasks)
        notStarted = sum(t.Status == TaskStatus.NOT_STARTED.value for t in tasks)
        today = date.today()
        overdue = sum(t.DueDate is not None and t.DueDate < today and t.Status != TaskStatus.COMPLETED.value for t in tasks)
        dueToday = sum(t.DueDate == today and t.Status != TaskStatus.COMPLETED.value for t in tasks)
        highPriority = sum(t.Priority == TaskPriority.HIGH.value for t in tasks)
        return {
            "total": total,
            "completed": completed,
            "inProgress": inProgress,
            "notStarted": notStarted,
            "completedPercent": round((completed / total * 100.0), 2) if total else 0.0,
            "HistoryCount": HistoryCount,
            "overdue": overdue,
            "today": dueToday,
            "highPriority": highPriority,
        }

    def getStatusDistribution(self, tasks: list[Task]) -> dict:
        """Возвращает количество задач в каждом статусе."""
        return {
            TaskStatus.NOT_STARTED.value: sum(t.Status == TaskStatus.NOT_STARTED.value for t in tasks),
            TaskStatus.IN_PROGRESS.value: sum(t.Status == TaskStatus.IN_PROGRESS.value for t in tasks),
            TaskStatus.COMPLETED.value: sum(t.Status == TaskStatus.COMPLETED.value for t in tasks),
        }

    def getPriorityDistribution(self, tasks: list[Task]) -> dict:
        """Возвращает распределение задач по приоритету."""
        return {p.value: sum(t.Priority == p.value for t in tasks) for p in TaskPriority}

    def getCompletionRate(self, tasks: list[Task]) -> float:
        """Возвращает процент завершённых задач."""
        return self.getSummary(tasks)["completedPercent"]

    def getAverageCompletionTime(self, tasks: list[Task]) -> float | None:
        """Возвращает среднее время завершения задач в минутах."""
        durations = [((t.CompletedAt - t.CreatedAt).total_seconds() / 60.0) for t in tasks if t.CompletedAt]
        return round(sum(durations) / len(durations), 2) if durations else None

    def getDeadlineDistribution(self, tasks: list[Task]) -> dict:
        """Возвращает распределение дедлайнов по активным (незавершённым) задачам."""
        ActiveTasks = [t for t in tasks if t.Status != TaskStatus.COMPLETED.value]
        today = date.today()
        week = today + timedelta(days=7)
        return {
            "overdue": sum(t.DueDate is not None and t.DueDate < today for t in ActiveTasks),
            "today": sum(t.DueDate == today for t in ActiveTasks),
            "next_7_days": sum(t.DueDate is not None and today < t.DueDate <= week for t in ActiveTasks),
            "no_deadline": sum(t.DueDate is None for t in ActiveTasks),
        }

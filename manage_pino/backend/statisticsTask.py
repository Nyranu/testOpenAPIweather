"""
ЫЫЫ СТАТИСТИКА, в общем прикольная и веселая штука которую я уже ненавижу, пожалуйста используй ее хотя бы раз, или УДАЛИ К ЧЕРТЯМ
Учти что дает она статистику именно из списка который ты ей дал
"""


from __future__ import annotations
from datetime import date, timedelta

from .models import Task, TaskPriority, TaskStatus

# Расчет статистики по задачам
class Statistics:

    # Дает основную сводку по задачам и истории
    def getSummary(self, tasks: list[Task], HistoryCount: int = 0) -> dict:
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
    # Дает количество задач в каждом статусе
    def getStatusDistribution(self, tasks: list[Task]) -> dict:
        return {
            TaskStatus.NOT_STARTED.value: sum(t.Status == TaskStatus.NOT_STARTED.value for t in tasks),
            TaskStatus.IN_PROGRESS.value: sum(t.Status == TaskStatus.IN_PROGRESS.value for t in tasks),
            TaskStatus.COMPLETED.value: sum(t.Status == TaskStatus.COMPLETED.value for t in tasks),
        }
    # Дает распределенные задачи по приоритетам уже
    def getPriorityDistribution(self, tasks: list[Task]) -> dict:
        return {p.value: sum(t.Priority == p.value for t in tasks) for p in TaskPriority}
    # Дает процент завершенных задач
    def getCompletionRate(self, tasks: list[Task]) -> float:
        return self.getSummary(tasks)["completedPercent"]
    # Дает средние вермя завершения задач в мин
    def getAverageCompletionTime(self, tasks: list[Task]) -> float | None:
        durations = [((t.CompletedAt - t.CreatedAt).total_seconds() / 60.0) for t in tasks if t.CompletedAt]
        return round(sum(durations) / len(durations), 2) if durations else None
    # Ох в общем тут возвращает дедлайны по активным и незавершенным задачам
    def getDeadlineDistribution(self, tasks: list[Task]) -> dict:
        ActiveTasks = [t for t in tasks if t.Status != TaskStatus.COMPLETED.value]
        today = date.today()
        week = today + timedelta(days=7)
        return {
            "overdue": sum(t.DueDate is not None and t.DueDate < today for t in ActiveTasks),
            "today": sum(t.DueDate == today for t in ActiveTasks),
            "next7Days": sum(t.DueDate is not None and today < t.DueDate <= week for t in ActiveTasks),
            "noDeadline": sum(t.DueDate is None for t in ActiveTasks),
        }

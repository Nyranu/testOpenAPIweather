from __future__ import annotations

from datetime import date, timedelta

from .models import Task, TaskPriority, TaskStatus


class StatisticsService:
    def get_summary(self, tasks: list[Task], history_count: int = 0) -> dict:
        total = len(tasks)
        completed = sum(t.status == TaskStatus.COMPLETED.value for t in tasks)
        in_progress = sum(t.status == TaskStatus.IN_PROGRESS.value for t in tasks)
        not_started = sum(t.status == TaskStatus.NOT_STARTED.value for t in tasks)
        today = date.today()
        overdue = sum(t.due_date is not None and t.due_date < today and t.status != TaskStatus.COMPLETED.value for t in tasks)
        due_today = sum(t.due_date == today and t.status != TaskStatus.COMPLETED.value for t in tasks)
        high_priority = sum(t.priority == TaskPriority.HIGH.value for t in tasks)
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "completed_percent": round((completed / total * 100.0), 2) if total else 0.0,
            "history_count": history_count,
            "overdue": overdue,
            "today": due_today,
            "high_priority": high_priority,
        }

    def get_status_distribution(self, tasks: list[Task]) -> dict:
        return {
            TaskStatus.NOT_STARTED.value: sum(t.status == TaskStatus.NOT_STARTED.value for t in tasks),
            TaskStatus.IN_PROGRESS.value: sum(t.status == TaskStatus.IN_PROGRESS.value for t in tasks),
            TaskStatus.COMPLETED.value: sum(t.status == TaskStatus.COMPLETED.value for t in tasks),
        }

    def get_priority_distribution(self, tasks: list[Task]) -> dict:
        return {p.value: sum(t.priority == p.value for t in tasks) for p in TaskPriority}

    def get_completion_rate(self, tasks: list[Task]) -> float:
        return self.get_summary(tasks)["completed_percent"]

    def get_average_completion_time(self, tasks: list[Task]) -> float | None:
        durations = [((t.completed_at - t.created_at).total_seconds() / 60.0) for t in tasks if t.completed_at]
        return round(sum(durations) / len(durations), 2) if durations else None

    def get_deadline_distribution(self, tasks: list[Task]) -> dict:
        today = date.today()
        week = today + timedelta(days=7)
        return {
            "overdue": sum(t.due_date is not None and t.due_date < today for t in tasks),
            "today": sum(t.due_date == today for t in tasks),
            "next_7_days": sum(t.due_date is not None and today < t.due_date <= week for t in tasks),
            "no_deadline": sum(t.due_date is None for t in tasks),
        }

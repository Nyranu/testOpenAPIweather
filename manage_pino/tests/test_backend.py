from datetime import datetime, date, timedelta
from pathlib import Path

import pytest


from backend.adapters import _parse_date
from backend.charts import ChartService
from backend.exceptions import InvalidPriorityError, InvalidStatusError, ValidationError
from backend.models import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from backend.repositories import InMemoryHistoryRepository, InMemoryTaskRepository
from backend.services import HistoryService, TaskService
from backend.statistics import StatisticsService
from backend.time_management import TimeManagementService


def build_service():
    hs = HistoryService(InMemoryHistoryRepository())
    return TaskService(InMemoryTaskRepository(), hs), hs


def test_create_task():
    svc, _ = build_service()
    task = svc.create_task(TaskCreate(title="A"))
    assert task.id == 1


def test_empty_title_forbidden():
    svc, _ = build_service()
    with pytest.raises(ValidationError):
        svc.create_task(TaskCreate(title="  "))


def test_parse_date_from_datetime_returns_date():
    parsed = _parse_date(datetime.now())
    assert isinstance(parsed, date)
    assert not isinstance(parsed, datetime)


def test_create_completed_task_sets_completed_at():
    svc, _ = build_service()
    task = svc.create_task(TaskCreate(title="A", status=TaskStatus.COMPLETED.value))
    assert task.completed_at is not None


def test_invalid_estimated_minutes_on_create():
    svc, _ = build_service()
    with pytest.raises(ValidationError):
        svc.create_task(TaskCreate(title="A", estimated_minutes=-10))


def test_invalid_status_and_priority_filters():
    svc, _ = build_service()
    svc.create_task(TaskCreate(title="A"))
    with pytest.raises(InvalidStatusError):
        svc.list_tasks(status="invalid")
    with pytest.raises(InvalidPriorityError):
        svc.list_tasks(priority="invalid")


def test_update_delete_status_completed_and_clearing_fields():
    svc, _ = build_service()
    task = svc.create_task(
        TaskCreate(title="A", due_date=date.today(), estimated_minutes=30, tags=["x"])
    )

    updated = svc.update_task(task.id, TaskUpdate(title="  B  ", description="C", tags=["t1", "t2"]))
    assert updated.title == "B"
    assert updated.description == "C"
    assert updated.tags == ["t1", "t2"]

    cleared = svc.update_task(task.id, TaskUpdate(clear_due_date=True, clear_estimated_minutes=True))
    assert cleared.due_date is None
    assert cleared.estimated_minutes is None

    done = svc.complete_task(task.id)
    assert done.status == TaskStatus.COMPLETED.value
    assert done.completed_at is not None

    reopened = svc.reopen_task(task.id)
    assert reopened.completed_at is None

    with pytest.raises(ValidationError):
        svc.update_task(task.id, TaskUpdate(estimated_minutes=0))

    assert svc.delete_task(task.id)


def test_statistics_empty_multi_and_deadline_distribution_excludes_completed():
    stats = StatisticsService()
    assert stats.get_summary([])["completed_percent"] == 0.0

    today = date.today()
    overdue_completed = TaskCreate(
        title="done",
        status=TaskStatus.COMPLETED.value,
        due_date=today - timedelta(days=2),
        priority=TaskPriority.HIGH.value,
    )
    active_overdue = TaskCreate(
        title="active",
        status=TaskStatus.IN_PROGRESS.value,
        due_date=today - timedelta(days=1),
    )

    svc, hs = build_service()
    svc.create_task(overdue_completed)
    svc.create_task(active_overdue)

    summary = stats.get_summary(svc.list_tasks(), len(hs.list_history(100)))
    assert summary["total"] == 2 and summary["completed"] == 1

    deadline = stats.get_deadline_distribution(svc.list_tasks())
    assert deadline["overdue"] == 1


@pytest.mark.skipif(__import__("importlib").util.find_spec("matplotlib") is None, reason="matplotlib not installed")
def test_time_management_and_chart(tmp_path):
    svc, _ = build_service()
    svc.create_task(TaskCreate(title="Overdue", due_date=date.today() - timedelta(days=1), estimated_minutes=50))
    svc.create_task(TaskCreate(title="Today", due_date=date.today(), estimated_minutes=50))

    tm = TimeManagementService()
    tasks = svc.list_tasks()
    assert len(tm.get_overdue_tasks(tasks)) == 1

    plan = tm.suggest_daily_plan(tasks, available_minutes=60)
    assert len(plan) == 1

    chart_path = ChartService().create_status_pie_chart(tasks, str(tmp_path))
    assert Path(chart_path).exists()

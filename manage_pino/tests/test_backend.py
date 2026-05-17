from datetime import date, timedelta

from backend.charts import ChartService
from backend.exceptions import ValidationError
from backend.models import TaskCreate, TaskStatus, TaskUpdate
from backend.repositories import InMemoryHistoryRepository, InMemoryTaskRepository
from backend.services import HistoryService, TaskService
from backend.statistics import StatisticsService
from backend.time_management import TimeManagementService


def build_service():
    hs = HistoryService(InMemoryHistoryRepository())
    return TaskService(InMemoryTaskRepository(), hs), hs


def test_create_task():
    svc, _ = build_service()
    t = svc.create_task(TaskCreate(title="A"))
    assert t.id == 1


def test_empty_title_forbidden():
    svc, _ = build_service()
    try:
        svc.create_task(TaskCreate(title="  "))
        assert False
    except ValidationError:
        assert True


def test_update_delete_status_and_completed_at():
    svc, _ = build_service()
    t = svc.create_task(TaskCreate(title="A"))
    t2 = svc.update_task(t.id, TaskUpdate(description="B"))
    assert t2.description == "B"
    done = svc.complete_task(t.id)
    assert done.status == TaskStatus.COMPLETED.value and done.completed_at is not None
    reopened = svc.reopen_task(t.id)
    assert reopened.completed_at is None
    assert svc.delete_task(t.id)


def test_statistics_empty_and_multi():
    stats = StatisticsService()
    assert stats.get_summary([])["completed_percent"] == 0.0
    svc, hs = build_service()
    svc.create_task(TaskCreate(title="1", status=TaskStatus.COMPLETED.value))
    svc.create_task(TaskCreate(title="2", status=TaskStatus.IN_PROGRESS.value))
    summary = stats.get_summary(svc.list_tasks(), len(hs.list_history(100)))
    assert summary["total"] == 2 and summary["completed"] == 1


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
    assert chart_path

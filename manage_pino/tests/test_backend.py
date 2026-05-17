from datetime import date, datetime, timedelta
from pathlib import Path
import importlib

import pytest

from backend.adapters import _parseDate, frontendTupleToTask, taskToFrontendTuple, tasksToFrontendTuples
from backend.charts import Charts
from backend.exceptions import InvalidPriorityError, InvalidStatusError, ValidationError
from backend.models import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from backend.repositories import InMemoryHistoryRepo, InMemoryTaskRepo
from backend.services import History, TaskManager
from backend.statistics import Statistics
from backend.time_management import TimeManagement


def buildService():
    HistoryInstance = History(InMemoryHistoryRepo())
    return TaskManager(InMemoryTaskRepo(), HistoryInstance), HistoryInstance


def test_adapters_roundtrip():
    TaskItem = frontendTupleToTask(("A", "B", TaskStatus.NOT_STARTED.value, "2026-05-17"))
    Tup = taskToFrontendTuple(TaskItem)
    assert Tup[0] == "A"
    assert len(tasksToFrontendTuples([TaskItem])) == 1


def test_createTask():
    TaskManagerInstance, _ = buildService()
    TaskItem = TaskManagerInstance.createTask(TaskCreate(Title="A"))
    assert TaskItem.Id == 1


def test_empty_title_forbidden():
    TaskManagerInstance, _ = buildService()
    with pytest.raises(ValidationError):
        TaskManagerInstance.createTask(TaskCreate(Title="  "))


def test_parseDate_from_datetime_returns_date():
    Parsed = _parseDate(datetime.now())
    assert isinstance(Parsed, date)
    assert not isinstance(Parsed, datetime)


def test_create_completed_task_sets_CompletedAt():
    TaskManagerInstance, _ = buildService()
    TaskItem = TaskManagerInstance.createTask(TaskCreate(Title="A", Status=TaskStatus.COMPLETED.value))
    assert TaskItem.CompletedAt is not None


def test_invalid_EstimatedMinutes_on_create():
    TaskManagerInstance, _ = buildService()
    with pytest.raises(ValidationError):
        TaskManagerInstance.createTask(TaskCreate(Title="A", EstimatedMinutes=-10))


def test_invalid_status_and_priority_filters():
    TaskManagerInstance, _ = buildService()
    TaskManagerInstance.createTask(TaskCreate(Title="A"))
    with pytest.raises(InvalidStatusError):
        TaskManagerInstance.listTasks(Status="invalid")
    with pytest.raises(InvalidPriorityError):
        TaskManagerInstance.listTasks(Priority="invalid")


def test_update_delete_status_completed_and_clearing_fields():
    TaskManagerInstance, _ = buildService()
    TaskItem = TaskManagerInstance.createTask(TaskCreate(Title="A", DueDate=date.today(), EstimatedMinutes=30, Tags=["x"]))

    DoneItem = TaskManagerInstance.completeTask(TaskItem.Id)
    assert DoneItem.CompletedAt is not None

    ReopenedItem = TaskManagerInstance.reopenTask(TaskItem.Id)
    assert ReopenedItem.CompletedAt is None

    with pytest.raises(ValidationError):
        TaskManagerInstance.updateTask(TaskItem.Id, TaskUpdate(EstimatedMinutes=0))

    ClearedItem = TaskManagerInstance.updateTask(TaskItem.Id, TaskUpdate(ClearDueDate=True, ClearEstimatedMinutes=True))
    assert ClearedItem.DueDate is None
    assert ClearedItem.EstimatedMinutes is None

    assert TaskManagerInstance.deleteTask(TaskItem.Id) is True


def test_statistics_and_time_management_keys():
    StatisticsObj = Statistics()
    TaskManagerInstance, HistoryInstance = buildService()
    TaskManagerInstance.createTask(TaskCreate(Title="active", Status=TaskStatus.IN_PROGRESS.value, DueDate=date.today() - timedelta(days=1)))
    Summary = StatisticsObj.getSummary(TaskManagerInstance.listTasks(), HistoryCount=len(HistoryInstance.listHistory(Limit=100)))
    assert Summary["total"] == 1
    Deadline = StatisticsObj.getDeadlineDistribution(TaskManagerInstance.listTasks())
    assert "next7Days" in Deadline and "noDeadline" in Deadline
    Urgency = TimeManagement().getTaskUrgency(TaskManagerInstance.listTasks()[0])
    assert Urgency in {"overdue", "today", "soon", "normal", "completed"}


@pytest.mark.skipif(importlib.util.find_spec("matplotlib") is None, reason="matplotlib not installed")
def test_charts_and_workload(tmp_path):
    TaskManagerInstance, _ = buildService()
    TaskManagerInstance.createTask(TaskCreate(Title="Overdue", DueDate=date.today() - timedelta(days=1), EstimatedMinutes=50))
    Tasks = TaskManagerInstance.listTasks()
    ChartsObj = Charts()
    Path1 = ChartsObj.createStatusPieChart(Tasks, OutputPath=str(tmp_path))
    Path2 = ChartsObj.createWorkloadChart(Tasks, Days=7, OutputPath=str(tmp_path))
    assert Path(Path1).exists() and Path(Path2).exists()


def test_example_usage_importable():
    importlib.import_module("backend.example_usage")

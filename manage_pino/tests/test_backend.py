from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from backend.adapters import _parseDate
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

    UpdatedItem = TaskManagerInstance.updateTask(TaskItem.Id, TaskUpdate(Title="  B  ", Description="C", Tags=["t1", "t2"]))
    assert UpdatedItem.Title == "B"
    assert UpdatedItem.Description == "C"
    assert UpdatedItem.Tags == ["t1", "t2"]

    ClearedItem = TaskManagerInstance.updateTask(TaskItem.Id, TaskUpdate(ClearDueDate=True, ClearEstimatedMinutes=True))
    assert ClearedItem.DueDate is None
    assert ClearedItem.EstimatedMinutes is None

    DoneItem = TaskManagerInstance.completeTask(TaskItem.Id)
    assert DoneItem.Status == TaskStatus.COMPLETED.value
    assert DoneItem.CompletedAt is not None

    ReopenedItem = TaskManagerInstance.reopenTask(TaskItem.Id)
    assert ReopenedItem.CompletedAt is None

    with pytest.raises(ValidationError):
        TaskManagerInstance.updateTask(TaskItem.Id, TaskUpdate(EstimatedMinutes=0))

    assert TaskManagerInstance.deleteTask(TaskItem.Id)


def test_statistics_empty_multi_and_deadline_distribution_excludes_completed():
    StatisticsObj = Statistics()
    assert StatisticsObj.getSummary([])["completedPercent"] == 0.0

    Today = date.today()
    OverdueCompleted = TaskCreate(Title="done", Status=TaskStatus.COMPLETED.value, DueDate=Today - timedelta(days=2), Priority=TaskPriority.HIGH.value)
    ActiveOverdue = TaskCreate(Title="active", Status=TaskStatus.IN_PROGRESS.value, DueDate=Today - timedelta(days=1))

    TaskManagerInstance, HistoryInstance = buildService()
    TaskManagerInstance.createTask(OverdueCompleted)
    TaskManagerInstance.createTask(ActiveOverdue)

    Summary = StatisticsObj.getSummary(TaskManagerInstance.listTasks(), len(HistoryInstance.listHistory(100)))
    assert Summary["total"] == 2 and Summary["completed"] == 1

    Deadline = StatisticsObj.getDeadlineDistribution(TaskManagerInstance.listTasks())
    assert Deadline["overdue"] == 1


@pytest.mark.skipif(__import__("importlib").util.find_spec("matplotlib") is None, reason="matplotlib not installed")
def test_time_management_and_chart(tmp_path):
    TaskManagerInstance, _ = buildService()
    TaskManagerInstance.createTask(TaskCreate(Title="Overdue", DueDate=date.today() - timedelta(days=1), EstimatedMinutes=50))
    TaskManagerInstance.createTask(TaskCreate(Title="Today", DueDate=date.today(), EstimatedMinutes=50))

    TimeManagementObj = TimeManagement()
    Tasks = TaskManagerInstance.listTasks()
    assert len(TimeManagementObj.getOverdueTasks(Tasks)) == 1

    Plan = TimeManagementObj.suggestDailyPlan(Tasks, AvailableMinutes=60)
    assert len(Plan) == 1

    ChartPath = Charts().createStatusPieChart(Tasks, str(tmp_path))
    assert Path(ChartPath).exists()

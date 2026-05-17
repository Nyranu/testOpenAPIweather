"""
Пример ручного использования backend-ядра без PyQt6-фронтенда.
"""
from datetime import date, timedelta

from backend.charts import Charts
from backend.models import TaskCreate, TaskPriority, TaskStatus
from backend.repositories import InMemoryHistoryRepo, InMemoryTaskRepo
from backend.services import History, TaskManager
from backend.statistics import Statistics


def main() -> None:
    TaskRepoObj = InMemoryTaskRepo()
    HistoryRepoObj = InMemoryHistoryRepo()
    HistoryObj = History(HistoryRepoObj)
    TaskManagerObj = TaskManager(TaskRepoObj, HistoryObj)

    TaskManagerObj.createTask(TaskCreate(Title="Подготовить отчет", Description="Финансы", DueDate=date.today(), EstimatedMinutes=90))
    TaskManagerObj.createTask(TaskCreate(Title="Купить продукты", DueDate=date.today() + timedelta(days=1), Priority=TaskPriority.HIGH.value))
    TaskManagerObj.createTask(TaskCreate(Title="Прочитать книгу", Priority=TaskPriority.LOW.value))
    Task4 = TaskManagerObj.createTask(TaskCreate(Title="Сделать презентацию", DueDate=date.today() - timedelta(days=1), Status=TaskStatus.IN_PROGRESS.value))

    TaskManagerObj.completeTask(1)
    TaskManagerObj.deleteTask(Task4.Id)

    print("Tasks:")
    for TaskItem in TaskManagerObj.listTasks():
        print(TaskItem)

    print("\nHistory:")
    for Record in HistoryObj.listHistory(Limit=20):
        print(Record)

    Stats = Statistics().getSummary(TaskManagerObj.listTasks(), HistoryCount=len(HistoryObj.listHistory(Limit=1000)))
    print("\nStats:", Stats)

    try:
        ChartPath = Charts().createStatusPieChart(TaskManagerObj.listTasks())
        print("Chart:", ChartPath)
    except RuntimeError as Error:
        print("Chart skipped:", Error)


if __name__ == "__main__":
    main()

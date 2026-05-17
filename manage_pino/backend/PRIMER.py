"""
Пример ручного использования backend-ядра без PyQt6-фронтенда.
"""
from datetime import date, timedelta
from chartsTask import Charts
from statisticsTask import Statistics
from models import TaskCreate, TaskPriority, TaskStatus
from repomemory import InMemoryHistoryRepo, InMemoryTaskRepo
from services import History, TaskManager




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

    print("ЗАДАЧИ:")
    for TaskItem in TaskManagerObj.listTasks():
        print(TaskItem)

    print("\nХистори:")
    for Record in HistoryObj.listHistory(Limit=20):
        print(Record)

    Stats = Statistics().getSummary(TaskManagerObj.listTasks(), HistoryCount=len(HistoryObj.listHistory(Limit=1000)))
    print("\nСтатусы:", Stats)

    try:
        ChartPath = Charts().createStatusPieChart(TaskManagerObj.listTasks())
        print("Граф:", ChartPath)
    except RuntimeError as Error:
        print("увы:", Error)


if __name__ == "__main__":
    main()

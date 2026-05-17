"""
Пример ручного использования backend-ядра без PyQt6-фронтенда.

Запускать из папки manage_pino:

    python -m backend.example_usage

Файл показывает создание сервисов, операции с задачами, историю,
статистику и генерацию графика.
"""

from datetime import date, timedelta

from backend.charts import Charts
from backend.models import TaskCreate, TaskPriority, TaskStatus
from backend.repositories import InMemoryHistoryRepo, InMemoryTaskRepo
from backend.services import History, TaskManager
from backend.statistics import Statistics


def main() -> None:
    task_repo = InMemoryTaskRepo()
    history_repo = InMemoryHistoryRepo()
    HistoryObj = History(history_repo)
    service = TaskManager(task_repo, HistoryObj)

    service.createTask(TaskCreate(Title="Подготовить отчет", "Финансы", DueDate=date.today(), EstimatedMinutes=90))
    service.createTask(TaskCreate(Title="Купить продукты", DueDate=date.today() + timedelta(days=1), Priority=TaskPriority.HIGH.value))
    service.createTask(TaskCreate(Title="Прочитать книгу", Priority=TaskPriority.LOW.value))
    t4 = service.createTask(TaskCreate(Title="Сделать презентацию", DueDate=date.today() - timedelta(days=1), Status=TaskStatus.IN_PROGRESS.value))

    service.completeTask(1)
    service.deleteTask(t4.Id)

    print("Tasks:")
    for task in service.listTasks():
        print(task)

    print("\nHistory:")
    for record in HistoryObj.listHistory(limit=20):
        print(record)

    StatisticsObj = Statistics().getSummary(service.listTasks(), HistoryCount=len(HistoryObj.listHistory(1000)))
    print("\nStats:", stats)

    chart = Charts().createStatusPieChart(service.listTasks())
    print("Chart:", chart)


if __name__ == "__main__":
    main()

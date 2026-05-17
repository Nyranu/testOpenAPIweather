"""
Пример ручного использования backend-ядра без PyQt6-фронтенда.

Запускать из папки manage_pino:

    python -m backend.example_usage

Файл показывает создание сервисов, операции с задачами, историю,
статистику и генерацию графика.
"""

from datetime import date, timedelta

from backend.charts import ChartService
from backend.models import TaskCreate, TaskPriority, TaskStatus
from backend.repositories import InMemoryHistoryRepository, InMemoryTaskRepository
from backend.services import HistoryService, TaskService
from backend.statistics import StatisticsService


def main() -> None:
    task_repo = InMemoryTaskRepository()
    history_repo = InMemoryHistoryRepository()
    history_service = HistoryService(history_repo)
    service = TaskService(task_repo, history_service)

    service.create_task(TaskCreate("Подготовить отчет", "Финансы", due_date=date.today(), estimated_minutes=90))
    service.create_task(TaskCreate("Купить продукты", due_date=date.today() + timedelta(days=1), priority=TaskPriority.HIGH.value))
    service.create_task(TaskCreate("Прочитать книгу", priority=TaskPriority.LOW.value))
    t4 = service.create_task(TaskCreate("Сделать презентацию", due_date=date.today() - timedelta(days=1), status=TaskStatus.IN_PROGRESS.value))

    service.complete_task(1)
    service.delete_task(t4.id)

    print("Tasks:")
    for task in service.list_tasks():
        print(task)

    print("\nHistory:")
    for record in history_service.list_history(limit=20):
        print(record)

    stats = StatisticsService().get_summary(service.list_tasks(), history_count=len(history_service.list_history(1000)))
    print("\nStats:", stats)

    chart = ChartService().create_status_pie_chart(service.list_tasks())
    print("Chart:", chart)


if __name__ == "__main__":
    main()

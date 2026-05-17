from backend.adapters import tasks_to_frontend_tuples
from backend.models import TaskCreate
from backend.repositories import InMemoryHistoryRepository, InMemoryTaskRepository
from backend.services import HistoryService, TaskService


def frontend_like_flow():
    tasks_repo = InMemoryTaskRepository()
    history_repo = InMemoryHistoryRepository()
    history_service = HistoryService(history_repo)
    task_service = TaskService(tasks_repo, history_service)

    task_service.create_task(TaskCreate(title="Новая задача", description="Описание"))

    backend_tasks = task_service.list_tasks()
    frontend_tasks = tasks_to_frontend_tuples(backend_tasks)
    return frontend_tasks

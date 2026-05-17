"""
Пример того, как фронтенд может получать данные из backend-ядра.

Это не подключение к PyQt6, а демонстрация идеи:
backend хранит объекты Task, а фронтенд может получать кортежи
через функции adapters.py.
"""

from backend.adapters import tasksToFrontendTuples
from backend.models import TaskCreate
from backend.repositories import InMemoryHistoryRepo, InMemoryTaskRepo
from backend.services import History, TaskManager


def frontend_like_flow():
    tasks_repo = InMemoryTaskRepo()
    history_repo = InMemoryHistoryRepo()
    HistoryObj = History(history_repo)
    TaskManagerObj = TaskManager(tasks_repo, HistoryObj)

    TaskManagerObj.createTask(TaskCreate(Title="Новая задача", Description="Описание"))

    backend_tasks = TaskManagerObj.listTasks()
    frontend_tasks = tasksToFrontendTuples(backend_tasks)
    return frontend_tasks

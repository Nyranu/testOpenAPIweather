"""Пример получения фронтенд-кортежей из backend-ядра."""

from backend.adapters import tasksToFrontendTuples
from backend.models import TaskCreate
from backend.repositories import InMemoryHistoryRepo, InMemoryTaskRepo
from backend.services import History, TaskManager


def frontendLikeFlow():
    TaskRepoObj = InMemoryTaskRepo()
    HistoryRepoObj = InMemoryHistoryRepo()
    HistoryObj = History(HistoryRepoObj)
    TaskManagerObj = TaskManager(TaskRepoObj, HistoryObj)

    TaskManagerObj.createTask(TaskCreate(Title="Новая задача", Description="Описание"))

    BackendTasks = TaskManagerObj.listTasks()
    FrontendTasks = tasksToFrontendTuples(BackendTasks)
    return FrontendTasks

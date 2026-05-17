"""
Файл exceptions.py.

Здесь собраны пользовательские исключения backend-ядра задач.

Используйте эти ошибки в сервисах вместо общих Exception,
чтобы фронтенд и тесты могли точно понимать тип проблемы.
"""


class TaskError(Exception):
    """Базовая ошибка backend-ядра задач."""


class TaskNotFoundError(TaskError):
    """Ошибка: задача с указанным id не найдена."""


class ValidationError(TaskError):
    """Ошибка: переданы некорректные данные задачи."""


class InvalidStatusError(ValidationError):
    """Ошибка: передан статус, которого нет в TaskStatus."""


class InvalidPriorityError(ValidationError):
    """Ошибка: передан приоритет, которого нет в TaskPriority."""

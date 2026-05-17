"""
исключения
"""

class TaskError(Exception):
    """Базовая ошибка"""

class TaskNotFoundError(TaskError):
    """Ошибка задачи с id"""

class ValidationError(TaskError):
    """Предеча неккоректных данных"""

class InvalidStatusError(ValidationError):
    """Передача несуществующего статуса"""

class InvalidPriorityError(ValidationError):
    """Передача несуществующего приоритета"""

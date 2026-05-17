class TaskError(Exception):
    """Base error for task backend."""


class TaskNotFoundError(TaskError):
    pass


class ValidationError(TaskError):
    pass


class InvalidStatusError(ValidationError):
    pass


class InvalidPriorityError(ValidationError):
    pass

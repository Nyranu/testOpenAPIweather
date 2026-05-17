"""
Пакет backend.

Этот файл собирает основные классы backend-ядра в одном месте.
Благодаря этому другие части проекта могут делать короткие импорты:

    from backend import TaskManager, TaskCreate

Здесь не должно быть бизнес-логики — только реэкспорт.
"""

# Явные импорты для основных сервисов.
from .charts import Charts
from .services import History, TaskManager
from .statistics import Statistics
from .time_management import TimeManagement

# Wildcard-реэкспорты оставлены для совместимости с ранним API пакета.
from .adapters import *
from .exceptions import *
from .models import *
from .repositories import *

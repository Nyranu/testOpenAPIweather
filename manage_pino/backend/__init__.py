"""
Пакет backend.

Этот файл собирает основные классы backend-ядра в одном месте.
Благодаря этому другие части проекта могут делать короткие импорты:

    from backend import TaskService, TaskCreate

Здесь не должно быть бизнес-логики — только реэкспорт.
"""

# Явные импорты для основных сервисов.
from .charts import ChartService
from .services import HistoryService, TaskService
from .statistics import StatisticsService
from .time_management import TimeManagementService

# Wildcard-реэкспорты оставлены для совместимости с ранним API пакета.
from .adapters import *
from .exceptions import *
from .models import *
from .repositories import *

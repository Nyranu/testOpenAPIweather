"""
Файл charts.py.

Здесь находится сервис построения графиков по задачам через matplotlib.
Сервис не запускает GUI и сохраняет графики в PNG-файлы.
"""

from __future__ import annotations

from pathlib import Path

from .models import Task
from .statistics import Statistics
from .time_management import TimeManagement

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    matplotlib = None
    plt = None


class Charts:
    """Сервис построения и сохранения графиков по задачам."""

    def __init__(self) -> None:
        """Инициализирует зависимости для расчётов графиков."""
        if plt is None:
            raise RuntimeError("Для создания графиков требуется matplotlib")
        self.StatisticsObj = Statistics()
        self.tm = TimeManagement()

    def _outputFile(self, name: str, OutputPath: str | None) -> Path:
        """Возвращает путь для файла графика и создаёт папку при необходимости."""
        base = Path(OutputPath) if OutputPath else Path(__file__).resolve().parent / "output" / "charts"
        base.mkdir(parents=True, exist_ok=True)
        return base / name

    def _emptyPlot(self, Title: str, path: Path) -> str:
        """Создаёт пустой график с подписью об отсутствии данных."""
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        plt.Title(title)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def createStatusPieChart(self, tasks: list[Task], OutputPath: str | None = None) -> str:
        """Строит круговую диаграмму распределения задач по статусам."""
        path = self._outputFile("status_pie.png", OutputPath)
        data = self.stats.getStatusDistribution(tasks)
        if not any(data.values()):
            return self._emptyPlot("Распределение по статусам", path)

        plt.figure(figsize=(6, 4))
        plt.pie(data.values(), labels=data.keys(), autopct="%1.0f%%")
        plt.Title("Распределение по статусам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def createPriorityBarChart(self, tasks: list[Task], OutputPath: str | None = None) -> str:
        """Строит столбчатый график распределения по приоритетам."""
        path = self._outputFile("priority_bar.png", OutputPath)
        data = self.stats.getPriorityDistribution(tasks)
        if not any(data.values()):
            return self._emptyPlot("Распределение по приоритетам", path)

        plt.figure(figsize=(6, 4))
        plt.bar(list(data.keys()), list(data.values()))
        plt.Title("Распределение по приоритетам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def createDeadlineBarChart(self, tasks: list[Task], OutputPath: str | None = None) -> str:
        """Строит столбчатый график распределения задач по категориям дедлайна."""
        path = self._outputFile("deadline_bar.png", OutputPath)
        data = self.stats.getDeadlineDistribution(tasks)
        if not any(data.values()):
            return self._emptyPlot("Распределение по дедлайнам", path)

        plt.figure(figsize=(6, 4))
        plt.bar(list(data.keys()), list(data.values()))
        plt.Title("Распределение по дедлайнам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def createWorkloadChart(self, tasks: list[Task], days: int = 7, OutputPath: str | None = None) -> str:
        """Строит линейный график ожидаемой нагрузки по дням."""
        path = self._outputFile("workload.png", OutputPath)
        data = self.tm.getWorkloadByDay(tasks, days)
        if not any(data.values()):
            return self._emptyPlot("Нагрузка по дням", path)

        plt.figure(figsize=(8, 4))
        plt.plot(list(data.keys()), list(data.values()), marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.Title("Нагрузка по дням")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

from __future__ import annotations

from pathlib import Path

from .models import Task
from .statistics import StatisticsService
from .time_management import TimeManagementService

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    matplotlib = None
    plt = None


class ChartService:
    """Сервис построения и сохранения графиков по задачам."""

    def __init__(self) -> None:
        """Инициализирует зависимости для расчётов графиков."""
        if plt is None:
            raise RuntimeError("Для создания графиков требуется matplotlib")
        self.stats = StatisticsService()
        self.tm = TimeManagementService()

    def _output_file(self, name: str, output_path: str | None) -> Path:
        """Возвращает путь для файла графика и создаёт папку при необходимости."""
        base = Path(output_path) if output_path else Path(__file__).resolve().parent / "output" / "charts"
        base.mkdir(parents=True, exist_ok=True)
        return base / name

    def _empty_plot(self, title: str, path: Path) -> str:
        """Создаёт пустой график с подписью об отсутствии данных."""
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        plt.title(title)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def create_status_pie_chart(self, tasks: list[Task], output_path: str | None = None) -> str:
        """Строит круговую диаграмму распределения задач по статусам."""
        path = self._output_file("status_pie.png", output_path)
        data = self.stats.get_status_distribution(tasks)
        if not any(data.values()):
            return self._empty_plot("Распределение по статусам", path)

        plt.figure(figsize=(6, 4))
        plt.pie(data.values(), labels=data.keys(), autopct="%1.0f%%")
        plt.title("Распределение по статусам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def create_priority_bar_chart(self, tasks: list[Task], output_path: str | None = None) -> str:
        """Строит столбчатый график распределения по приоритетам."""
        path = self._output_file("priority_bar.png", output_path)
        data = self.stats.get_priority_distribution(tasks)
        if not any(data.values()):
            return self._empty_plot("Распределение по приоритетам", path)

        plt.figure(figsize=(6, 4))
        plt.bar(list(data.keys()), list(data.values()))
        plt.title("Распределение по приоритетам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def create_deadline_bar_chart(self, tasks: list[Task], output_path: str | None = None) -> str:
        """Строит столбчатый график распределения задач по категориям дедлайна."""
        path = self._output_file("deadline_bar.png", output_path)
        data = self.stats.get_deadline_distribution(tasks)
        if not any(data.values()):
            return self._empty_plot("Распределение по дедлайнам", path)

        plt.figure(figsize=(6, 4))
        plt.bar(list(data.keys()), list(data.values()))
        plt.title("Распределение по дедлайнам")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

    def create_workload_chart(self, tasks: list[Task], days: int = 7, output_path: str | None = None) -> str:
        """Строит линейный график ожидаемой нагрузки по дням."""
        path = self._output_file("workload.png", output_path)
        data = self.tm.get_workload_by_day(tasks, days)
        if not any(data.values()):
            return self._empty_plot("Нагрузка по дням", path)

        plt.figure(figsize=(8, 4))
        plt.plot(list(data.keys()), list(data.values()), marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title("Нагрузка по дням")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return str(path)

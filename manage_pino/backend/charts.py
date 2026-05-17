from __future__ import annotations

from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    matplotlib = None
    plt = None

from .statistics import StatisticsService
from .time_management import TimeManagementService


class ChartService:
    def __init__(self) -> None:
        self.stats = StatisticsService()
        self.tm = TimeManagementService()

    def _output_file(self, name: str, output_path: str | None) -> Path:
        base = Path(output_path) if output_path else Path(__file__).resolve().parent / "output" / "charts"
        base.mkdir(parents=True, exist_ok=True)
        return base / name

    def _empty_plot(self, title: str, path: Path) -> str:
        if plt is None:
            path.write_text(f"{title}: Нет данных", encoding="utf-8")
            return str(path)
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        plt.title(title)
        plt.axis("off")
        plt.tight_layout(); plt.savefig(path); plt.close()
        return str(path)

    def create_status_pie_chart(self, tasks, output_path=None) -> str:
        path = self._output_file("status_pie.png", output_path)
        data = self.stats.get_status_distribution(tasks)
        if plt is None or not any(data.values()):
            return self._empty_plot("Распределение по статусам", path)
        plt.figure(figsize=(6, 4)); plt.pie(data.values(), labels=data.keys(), autopct="%1.0f%%")
        plt.title("Распределение по статусам"); plt.tight_layout(); plt.savefig(path); plt.close(); return str(path)

    def create_priority_bar_chart(self, tasks, output_path=None) -> str:
        path = self._output_file("priority_bar.png", output_path)
        data = self.stats.get_priority_distribution(tasks)
        if plt is None or not any(data.values()):
            return self._empty_plot("Распределение по приоритетам", path)
        plt.figure(figsize=(6, 4)); plt.bar(list(data.keys()), list(data.values()))
        plt.title("Распределение по приоритетам"); plt.tight_layout(); plt.savefig(path); plt.close(); return str(path)

    def create_deadline_bar_chart(self, tasks, output_path=None) -> str:
        path = self._output_file("deadline_bar.png", output_path)
        data = self.stats.get_deadline_distribution(tasks)
        if plt is None or not any(data.values()):
            return self._empty_plot("Распределение по дедлайнам", path)
        plt.figure(figsize=(6, 4)); plt.bar(list(data.keys()), list(data.values()))
        plt.title("Распределение по дедлайнам"); plt.tight_layout(); plt.savefig(path); plt.close(); return str(path)

    def create_workload_chart(self, tasks, days=7, output_path=None) -> str:
        path = self._output_file("workload.png", output_path)
        data = self.tm.get_workload_by_day(tasks, days)
        if plt is None or not any(data.values()):
            return self._empty_plot("Нагрузка по дням", path)
        plt.figure(figsize=(8, 4)); plt.plot(list(data.keys()), list(data.values()), marker="o")
        plt.xticks(rotation=45, ha="right"); plt.title("Нагрузка по дням"); plt.tight_layout(); plt.savefig(path); plt.close(); return str(path)

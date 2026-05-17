"""
Я примерно сделал несколько заготовок для графиков через matplotlib, постарайся обойтись ими, он также сохраняет из в png может возвращать путь и тд
"""

from __future__ import annotations
from pathlib import Path
from .models import Task
from .statisticsTask import Statistics
from .timeManagement import TimeManagement

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    matplotlib = None
    plt = None

#Основной класс для вызова на построение и сохранение графиков
class Charts:

    def __init__(self) -> None:
        if plt is None:
            raise RuntimeError("Для создания графика нужек matplotlib")
        self.StatisticsObj = Statistics()
        self.TimeManagementObj = TimeManagement()

    #Возвращает путь для файла графика и делает папку если нужно
    def _outputFile(self, Name: str, OutputPath: str | None) -> Path:
        Base = Path(OutputPath) if OutputPath else Path(__file__).resolve().parent / "output" / "charts"
        Base.mkdir(parents=True, exist_ok=True)
        return Base / Name
    # Cоздает пустой график
    def _emptyPlot(self, Title: str, PathObj: Path) -> str:
        plt.figure(figsize=(6, 4))
        plt.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        plt.title(Title)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(PathObj)
        plt.close()
        return str(PathObj)

    # Строит круговою диаграмму - она распределяет задачи по статусам
    def createStatusPieChart(self, Tasks: list[Task], OutputPath: str | None = None) -> str:
        PathObj = self._outputFile("status_pie.png", OutputPath)
        Data = self.StatisticsObj.getStatusDistribution(Tasks)
        if not any(Data.values()):
            return self._emptyPlot("Распределение по статусам", PathObj)
        plt.figure(figsize=(6, 4))
        plt.pie(Data.values(), labels=Data.keys(), autopct="%1.0f%%")
        plt.title("Распределение по статусам")
        plt.tight_layout()
        plt.savefig(PathObj)
        plt.close()
        return str(PathObj)

    # Делает столбик - распределяет по приоритету
    def createPriorityBarChart(self, Tasks: list[Task], OutputPath: str | None = None) -> str:
        PathObj = self._outputFile("priority_bar.png", OutputPath)
        Data = self.StatisticsObj.getPriorityDistribution(Tasks)
        if not any(Data.values()):
            return self._emptyPlot("Распределение по приоритетам", PathObj)
        plt.figure(figsize=(6, 4))
        plt.bar(list(Data.keys()), list(Data.values()))
        plt.title("Распределение по приоритетам")
        plt.tight_layout()
        plt.savefig(PathObj)
        plt.close()
        return str(PathObj)

    #  Делает также стобик но распределеяет уже по дедлайну
    def createDeadlineBarChart(self, Tasks: list[Task], OutputPath: str | None = None) -> str:
        PathObj = self._outputFile("deadline_bar.png", OutputPath)
        Data = self.StatisticsObj.getDeadlineDistribution(Tasks)
        if not any(Data.values()):
            return self._emptyPlot("Распределение по дедлайнам", PathObj)
        plt.figure(figsize=(6, 4))
        plt.bar(list(Data.keys()), list(Data.values()))
        plt.title("Распределение по дедлайнам")
        plt.tight_layout()
        plt.savefig(PathObj)
        plt.close()
        return str(PathObj)

    # Строит линейный график - какая нагрузка будет на данный день/дни
    def createWorkloadChart(self, Tasks: list[Task], Days: int = 7, OutputPath: str | None = None) -> str:
        PathObj = self._outputFile("workload.png", OutputPath)
        Data = self.TimeManagementObj.getWorkloadByDay(Tasks, Days)
        if not any(Data.values()):
            return self._emptyPlot("Нагрузка по дням", PathObj)
        plt.figure(figsize=(8, 4))
        plt.plot(list(Data.keys()), list(Data.values()), marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title("Нагрузка по дням")
        plt.tight_layout()
        plt.savefig(PathObj)
        plt.close()
        return str(PathObj)

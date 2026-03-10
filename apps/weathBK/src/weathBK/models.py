from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """Описание локации"""

    name: str
    latitude: float
    longitude: float
    country: str | None = None
    admin1: str | None = None


@dataclass(frozen=True)
class DailyForecast:
    """Нормализованная дневная запись"""

    date: str
    weather_code: int
    temp_min: float
    temp_max: float
    precipitation_probability_max: float
    wind_speed_max: float

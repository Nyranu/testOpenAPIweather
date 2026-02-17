from __future__ import annotations

from typing import Any

import requests

from weather_backend.models import DailyForecast, Location

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherApiError(RuntimeError):
    """Ошибка взаимодействия с погодным API."""


def _request_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """Выполняет GET-запрос и возвращает JSON с проверкой сетевых ошибок."""

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise WeatherApiError(f"Не удалось получить данные от API: {exc}") from exc


def geocode_address(address: str) -> Location:
    """Преобразует адрес в координаты и возвращает лучшую найденную локацию."""

    data = _request_json(
        GEOCODING_URL,
        {
            "name": address,
            "count": 1,
            "language": "ru",
            "format": "json",
        },
    )

    results = data.get("results") or []
    if not results:
        raise WeatherApiError("Адрес не найден. Попробуйте уточнить запрос.")

    best = results[0]
    return Location(
        name=best.get("name", "Unknown"),
        latitude=best["latitude"],
        longitude=best["longitude"],
        country=best.get("country"),
        admin1=best.get("admin1"),
    )


def get_daily_forecast(latitude: float, longitude: float, days: int = 7) -> list[DailyForecast]:
    """Получает ежедневный прогноз Open-Meteo на заданное число дней."""

    data = _request_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "weathercode,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,windspeed_10m_max"
            ),
            "forecast_days": days,
            "timezone": "auto",
        },
    )

    daily = data.get("daily")
    if not daily:
        raise WeatherApiError("API не вернуло ежедневный прогноз.")

    records = zip(
        daily["time"],
        daily["weathercode"],
        daily["temperature_2m_min"],
        daily["temperature_2m_max"],
        daily["precipitation_probability_max"],
        daily["windspeed_10m_max"],
    )

    return [
        DailyForecast(
            date=date,
            weather_code=weather_code,
            temp_min=temp_min,
            temp_max=temp_max,
            precipitation_probability_max=precipitation_probability,
            wind_speed_max=wind_max,
        )
        for date, weather_code, temp_min, temp_max, precipitation_probability, wind_max in records
    ]

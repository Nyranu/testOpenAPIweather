from __future__ import annotations

from typing import Any

import requests

from .models import DailyForecast, Location

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUIRED_DAILY_FIELDS = (
    "time",
    "weather_code",
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_probability_max",
    "wind_speed_10m_max",
)


class WeatherApiError(RuntimeError):
    """Ошибка взаимодействия с погодным API."""


def _request_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherApiError(f"Не удалось получить данные от API: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise WeatherApiError("API вернуло некорректный JSON.") from exc

    if isinstance(data, dict) and data.get("error") is True:
        reason = data.get("reason") or data.get("message") or "Неизвестная ошибка API"
        raise WeatherApiError(f"Ошибка API: {reason}")

    if not isinstance(data, dict):
        raise WeatherApiError("API вернуло неожиданный формат ответа.")

    return data


def geocode_address(address: str) -> Location:
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
    data = _request_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,wind_speed_10m_max"
            ),
            "forecast_days": days,
            "timezone": "auto",
        },
    )

    daily = data.get("daily")
    if not isinstance(daily, dict):
        raise WeatherApiError("API не вернуло блок daily в ожидаемом формате.")

    missing = [field for field in REQUIRED_DAILY_FIELDS if field not in daily]
    if missing:
        raise WeatherApiError(f"В ответе API отсутствуют обязательные поля daily: {', '.join(missing)}")

    records = zip(
        daily["time"],
        daily["weather_code"],
        daily["temperature_2m_min"],
        daily["temperature_2m_max"],
        daily["precipitation_probability_max"],
        daily["wind_speed_10m_max"],
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

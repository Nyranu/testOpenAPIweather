from weathBK.formatters import format_forecast, format_location, weather_code_to_text
from weathBK.models import DailyForecast, Location


def test_weather_code_to_text_known_code():
    assert weather_code_to_text(0) == "Ясно"


def test_weather_code_to_text_unknown_code():
    assert weather_code_to_text(999) == "Неизвестный код (999)"


def test_format_location_full():
    location = Location("Москва", 55.75, 37.61, "Россия", "Москва")
    assert format_location(location) == "Москва, Москва, Россия, (55.7500, 37.6100)"


def test_format_forecast():
    location = Location("Москва", 55.75, 37.61)
    forecast = [
        DailyForecast("2026-05-17", 0, 10.0, 20.0, 50.0, 12.4),
    ]

    text = format_forecast(location, forecast)

    assert "Прогноз для: Москва" in text
    assert "2026-05-17: Ясно" in text
    assert "Температура: 10.0°C .. 20.0°C" in text

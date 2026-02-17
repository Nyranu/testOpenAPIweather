from weather_backend.formatters import format_forecast
from weather_backend.models import DailyForecast, Location


def test_format_forecast_contains_key_fields() -> None:
    location = Location(name="Moscow", latitude=55.75, longitude=37.61, country="Russia")
    forecast = [
        DailyForecast(
            date="2026-02-17",
            weather_code=1,
            temp_min=-3.2,
            temp_max=1.4,
            precipitation_probability_max=35,
            wind_speed_max=18.5,
        )
    ]

    text = format_forecast(location, forecast)

    assert "Прогноз для:" in text
    assert "2026-02-17" in text
    assert "Температура:" in text
    assert "Осадки" in text

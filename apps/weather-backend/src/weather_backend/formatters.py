from weather_backend.models import DailyForecast, Location

WEATHER_CODE_MAP = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Иней/туман",
    51: "Лёгкая морось",
    53: "Морось",
    55: "Сильная морось",
    61: "Небольшой дождь",
    63: "Дождь",
    65: "Сильный дождь",
    71: "Небольшой снег",
    73: "Снег",
    75: "Сильный снег",
    80: "Ливни",
    95: "Гроза",
}


def weather_code_to_text(code: int) -> str:
    """Человекочитаемое описание погодного кода Open-Meteo."""

    return WEATHER_CODE_MAP.get(code, f"Неизвестный код ({code})")


def format_location(location: Location) -> str:
    """Собирает заголовок с информацией о выбранной локации."""

    parts = [location.name]
    if location.admin1:
        parts.append(location.admin1)
    if location.country:
        parts.append(location.country)
    parts.append(f"({location.latitude:.4f}, {location.longitude:.4f})")
    return ", ".join(parts)


def format_forecast(location: Location, forecast: list[DailyForecast]) -> str:
    """Формирует итоговый текстовый отчёт для консоли."""

    lines = [f"Прогноз для: {format_location(location)}", "-" * 72]
    for day in forecast:
        lines.extend(
            [
                f"{day.date}: {weather_code_to_text(day.weather_code)}",
                f"  Температура: {day.temp_min:.1f}°C .. {day.temp_max:.1f}°C",
                f"  Осадки (вероятность max): {day.precipitation_probability_max:.0f}%",
                f"  Ветер (max): {day.wind_speed_max:.1f} км/ч",
                "",
            ]
        )

    return "\n".join(lines).rstrip()

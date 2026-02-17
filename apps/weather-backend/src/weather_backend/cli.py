from weather_backend.api import WeatherApiError, geocode_address, get_daily_forecast
from weather_backend.formatters import format_forecast
from weather_backend.models import Location


def _read_float(prompt: str, min_value: float, max_value: float) -> float:
    """Чтение числа с проверкой диапазона."""

    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Введите корректное число.")
            continue

        if min_value <= value <= max_value:
            return value

        print(f"Значение должно быть в диапазоне [{min_value}; {max_value}].")


def _read_days() -> int:
    """Запрашивает число дней прогноза в допустимом диапазоне 5-7."""

    while True:
        raw = input("На сколько дней нужен прогноз? (5-7): ").strip()
        if raw.isdigit() and 5 <= int(raw) <= 7:
            return int(raw)
        print("Введите целое число от 5 до 7.")


def _input_location() -> Location:
    """Позволяет выбрать источник координат: прямой ввод или геокодинг адреса."""

    while True:
        print("Выберите способ ввода локации:")
        print("1 — По координатам (широта/долгота)")
        print("2 — По адресу")

        choice = input("Ваш выбор (1/2): ").strip()

        if choice == "1":
            lat = _read_float("Введите широту (-90..90): ", -90, 90)
            lon = _read_float("Введите долготу (-180..180): ", -180, 180)
            return Location(name="Координаты пользователя", latitude=lat, longitude=lon)

        if choice == "2":
            address = input("Введите адрес: ").strip()
            if not address:
                print("Адрес не должен быть пустым.")
                continue
            return geocode_address(address)

        print("Введите 1 или 2.")


def run_cli() -> None:
    """Основной сценарий консольного приложения."""

    print("=== Weather CLI Monolith (Open-Meteo) ===")

    try:
        location = _input_location()
        days = _read_days()
        forecast = get_daily_forecast(location.latitude, location.longitude, days=days)
        print()
        print(format_forecast(location, forecast))
    except WeatherApiError as exc:
        print(f"Ошибка работы с API: {exc}")

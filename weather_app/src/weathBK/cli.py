from .api import WeatherApiError, geocodeAddress, getDailyForecast
from .formatters import formatForecast
from .models import Location


def _readFloat(prompt: str, minValue: float, maxValue: float) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Введите корректное число.")
            continue

        if minValue <= value <= maxValue:
            return value

        print(f"Значение должно быть в диапазоне [{minValue}; {maxValue}].")


def _readDays() -> int:
    while True:
        raw = input("На сколько дней нужен прогноз? (1-7): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 7:
            return int(raw)
        print("Введите целое число от 1 до 7.")


def _inputLocation() -> Location:
    while True:
        print("Выберите способ ввода локации:")
        print("1 По координатам (широта/долгота)")
        print("2 По адресу")

        choice = input("Ваш выбор (1/2): ").strip()

        if choice == "1":
            lat = _readFloat("Введите широту (-90..90): ", -90, 90)
            lon = _readFloat("Введите долготу (-180..180): ", -180, 180)
            return Location(name="Координаты пользователя", latitude=lat, longitude=lon)

        if choice == "2":
            address = input("Введите адрес: ").strip()
            if not address:
                print("Адрес не должен быть пустым.")
                continue
            return geocodeAddress(address)

        print("Введите 1 или 2.")


def runCLI() -> None:
    print("=== Метеорологическая программа '"'Солнышко'"' ===")

    try:
        location = _inputLocation()
        days = _readDays()
        forecast = getDailyForecast(location.latitude, location.longitude, days=days)
        print()
        print(formatForecast(location, forecast))
    except WeatherApiError as exc:
        print(f"Ошибка работы с API: {exc}")

# weather_app

Простое консольное Python-приложение для получения прогноза погоды через Open-Meteo.

## Что умеет
- Получать прогноз по координатам.
- Искать локацию по адресу и получать прогноз.
- Выводить данные в удобном текстовом формате.

## Подготовка окружения

```bash
cd weather_app
python -m venv .venv
```

### Активация (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### Активация (Linux/macOS)

```bash
source .venv/bin/activate
```

## Установка зависимостей

```bash
python -m pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

## Тесты

```bash
pytest -q
```

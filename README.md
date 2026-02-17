# Weather Monolith + Turborepo

Pet-проект на Python для прогноза погоды на **5–7 дней** по:
- координатам (широта/долгота), или
- полному адресу (через геокодинг).

Используется открытый API [Open-Meteo](https://open-meteo.com/) без API-ключа.

## Что изменено по архитектуре

Проект адаптирован под **монолитную архитектуру**:
- один основной backend-сервис (`weather-backend`),
- единая доменная логика внутри одного Python-приложения,
- явное разделение на модули (`api`, `models`, `formatters`, `cli`) внутри одного сервиса.

При этом добавлен **Turborepo** для удобного управления задачами в репозитории:
- единые команды `dev/test/lint` из корня,
- масштабируемая структура на будущее (если позже появятся web-ui, worker и т.д.).

## Структура репозитория

```text
.
├── apps/
│   └── weather-backend/
│       ├── src/weather_backend/
│       │   ├── api.py
│       │   ├── cli.py
│       │   ├── formatters.py
│       │   └── models.py
│       ├── tests/
│       ├── app.py
│       ├── package.json
│       ├── pytest.ini
│       └── requirements.txt
├── package.json
└── turbo.json
```

## Установка

### 1) Python зависимости

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r apps/weather-backend/requirements.txt
```

### 2) Node зависимости (для Turborepo)

```bash
npm install
```

## Запуск

### Через Turborepo (рекомендуется)

```bash
npm run dev
```

### Напрямую Python

```bash
cd apps/weather-backend
PYTHONPATH=src python app.py
```

## Проверки

Из корня:

```bash
npm run lint
npm run test
```

Или напрямую в приложении:

```bash
cd apps/weather-backend
PYTHONPATH=src python -m compileall app.py src tests
PYTHONPATH=src pytest -q
```

## Консольный сценарий

1. Выберите `1` (координаты) или `2` (адрес).
2. Введите данные.
3. Укажите число дней прогноза от 5 до 7.
4. Получите форматированный прогноз по дням.

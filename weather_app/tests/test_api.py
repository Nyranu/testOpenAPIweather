from types import SimpleNamespace

import pytest

from weathBK.api import WeatherApiError, _request_json, geocode_address, get_daily_forecast


def test_geocode_address_success(monkeypatch):
    def fake_request_json(url, params):
        return {
            "results": [
                {
                    "name": "Moscow",
                    "latitude": 55.75,
                    "longitude": 37.61,
                    "country": "Russia",
                    "admin1": "Moscow",
                }
            ]
        }

    monkeypatch.setattr("weathBK.api._request_json", fake_request_json)
    location = geocode_address("Москва")

    assert location.name == "Moscow"
    assert location.latitude == 55.75


def test_geocode_address_not_found(monkeypatch):
    monkeypatch.setattr("weathBK.api._request_json", lambda url, params: {"results": []})

    with pytest.raises(WeatherApiError, match="Адрес не найден"):
        geocode_address("unknown")


def test_geocode_address_missing_coordinates_raises_weather_api_error(monkeypatch):
    monkeypatch.setattr(
        "weathBK.api._request_json",
        lambda url, params: {"results": [{"name": "Broken result"}]},
    )

    with pytest.raises(WeatherApiError, match="без координат"):
        geocode_address("broken")


def test_get_daily_forecast_success_with_current_open_meteo_keys(monkeypatch):
    def fake_request_json(url, params):
        return {
            "daily": {
                "time": ["2026-05-17"],
                "weather_code": [1],
                "temperature_2m_min": [11.0],
                "temperature_2m_max": [21.0],
                "precipitation_probability_max": [30.0],
                "wind_speed_10m_max": [15.0],
            }
        }

    monkeypatch.setattr("weathBK.api._request_json", fake_request_json)
    result = get_daily_forecast(55.75, 37.61, days=1)

    assert len(result) == 1
    assert result[0].weather_code == 1
    assert result[0].wind_speed_max == 15.0


def test_get_daily_forecast_missing_daily_raises_weather_api_error(monkeypatch):
    monkeypatch.setattr("weathBK.api._request_json", lambda url, params: {})

    with pytest.raises(WeatherApiError, match="daily"):
        get_daily_forecast(55.75, 37.61)


def test_get_daily_forecast_missing_required_field_raises_weather_api_error(monkeypatch):
    monkeypatch.setattr(
        "weathBK.api._request_json",
        lambda url, params: {
            "daily": {
                "time": ["2026-05-17"],
                "temperature_2m_min": [11.0],
                "temperature_2m_max": [21.0],
                "precipitation_probability_max": [30.0],
                "wind_speed_10m_max": [15.0],
            }
        },
    )

    with pytest.raises(WeatherApiError, match="обязательные поля"):
        get_daily_forecast(55.75, 37.61)


def test_get_daily_forecast_mismatched_daily_lengths_raises_weather_api_error(monkeypatch):
    monkeypatch.setattr(
        "weathBK.api._request_json",
        lambda url, params: {
            "daily": {
                "time": ["2026-05-17", "2026-05-18"],
                "weather_code": [1],
                "temperature_2m_min": [11.0, 12.0],
                "temperature_2m_max": [21.0, 22.0],
                "precipitation_probability_max": [30.0, 35.0],
                "wind_speed_10m_max": [15.0, 16.0],
            }
        },
    )

    with pytest.raises(WeatherApiError, match="разную длину"):
        get_daily_forecast(55.75, 37.61)


def test_request_json_api_error_payload_raises_weather_api_error(monkeypatch):
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"error": True, "reason": "bad query"},
    )
    monkeypatch.setattr("weathBK.api.requests.get", lambda *args, **kwargs: response)

    with pytest.raises(WeatherApiError, match="Ошибка API: bad query"):
        _request_json("http://example.com", {})


def test_request_json_invalid_json_raises_weather_api_error(monkeypatch):
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: (_ for _ in ()).throw(ValueError("invalid json")),
    )
    monkeypatch.setattr("weathBK.api.requests.get", lambda *args, **kwargs: response)

    with pytest.raises(WeatherApiError, match="некорректный JSON"):
        _request_json("http://example.com", {})


def test_request_json_non_dict_response_raises_weather_api_error(monkeypatch):
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: [1, 2, 3],
    )
    monkeypatch.setattr("weathBK.api.requests.get", lambda *args, **kwargs: response)

    with pytest.raises(WeatherApiError, match="неожиданный формат"):
        _request_json("http://example.com", {})

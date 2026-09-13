"""Tests for the weather service (mocked HTTP calls)."""
from unittest.mock import patch, MagicMock
import pytest

import services.weather_service as ws


MOCK_CURRENT = {
    "name": "Pune",
    "main": {"temp": 28.5, "feels_like": 30.0, "humidity": 72},
    "weather": [{"description": "partly cloudy"}],
    "wind": {"speed": 3.2},
}

MOCK_FORECAST_LIST = [
    {"weather": [{"description": "clear sky"}]},
    {"weather": [{"description": "light rain"}]},
]


def _make_mock_response(data):
    mock_resp = MagicMock()
    mock_resp.json.return_value = data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@patch("services.weather_service.httpx.get")
def test_get_weather_context_returns_string(mock_get):
    def side_effect(url, **kwargs):
        if "forecast" in url:
            return _make_mock_response({"list": MOCK_FORECAST_LIST})
        return _make_mock_response(MOCK_CURRENT)

    mock_get.side_effect = side_effect
    result = ws.get_weather_context("Pune")
    assert isinstance(result, str)
    assert "Pune" in result
    assert "28" in result


@patch("services.weather_service.httpx.get")
def test_get_weather_context_rain_forecast(mock_get):
    def side_effect(url, **kwargs):
        if "forecast" in url:
            return _make_mock_response({"list": MOCK_FORECAST_LIST})
        return _make_mock_response(MOCK_CURRENT)

    mock_get.side_effect = side_effect
    result = ws.get_weather_context("Pune")
    assert "Rain" in result or "rain" in result


@patch("services.weather_service.httpx.get")
def test_get_weather_context_empty_on_failure(mock_get):
    mock_get.side_effect = Exception("network error")
    result = ws.get_weather_context("InvalidCity")
    assert result == ""


def test_get_weather_context_empty_location():
    result = ws.get_weather_context("")
    assert result == ""


@patch("services.weather_service.httpx.get")
def test_get_weather_response_structure(mock_get):
    def side_effect(url, **kwargs):
        if "forecast" in url:
            return _make_mock_response({"list": MOCK_FORECAST_LIST})
        return _make_mock_response(MOCK_CURRENT)

    mock_get.side_effect = side_effect
    result = ws.get_weather_response("Pune")
    assert result["location"] == "Pune"
    assert result["temperature"] == 29  # rounded
    assert result["humidity"] == 72
    assert "forecast_summary" in result

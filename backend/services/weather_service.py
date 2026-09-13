"""
Weather Service
===============
Fetches current weather and a 5-day forecast from OpenWeatherMap and
formats the data as a concise context string for LLM prompt injection.
"""

from __future__ import annotations

import httpx
from config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(location: str) -> dict:
    """Fetch current weather for a location."""
    resp = httpx.get(
        f"{BASE_URL}/weather",
        params={
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        },
        timeout=8.0,
    )
    resp.raise_for_status()
    return resp.json()


def get_forecast(location: str) -> list[dict]:
    """Fetch 5-day / 3-hour forecast for a location (returns daily summaries)."""
    resp = httpx.get(
        f"{BASE_URL}/forecast",
        params={
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 8,  # next 24 hours (8 × 3h slots)
        },
        timeout=8.0,
    )
    resp.raise_for_status()
    return resp.json().get("list", [])


def get_weather_context(location: str) -> str:
    """
    Return a formatted weather summary string for LLM prompt injection.
    Returns empty string on any failure (graceful degradation).
    """
    if not location or not location.strip():
        return ""

    try:
        current = get_current_weather(location)
        forecast_list = get_forecast(location)

        city = current.get("name", location)
        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        humidity = current["main"]["humidity"]
        condition = current["weather"][0]["description"].capitalize()
        wind_speed = current["wind"]["speed"]

        # Summarise rainfall/conditions from next-24h forecast
        rain_expected = any(
            "rain" in slot.get("weather", [{}])[0].get("description", "").lower()
            for slot in forecast_list
        )
        forecast_note = "Rain is expected in the next 24 hours." if rain_expected else "No rain expected in the next 24 hours."

        return (
            f"Current weather in {city}: {temp:.0f}°C (feels like {feels_like:.0f}°C), "
            f"{condition}. Humidity: {humidity}%. Wind: {wind_speed} m/s. "
            f"{forecast_note}"
        )
    except Exception:
        return ""


def get_weather_response(location: str) -> dict:
    """
    Return structured weather data for the frontend weather widget.
    Raises httpx.HTTPStatusError on bad location.
    """
    current = get_current_weather(location)
    forecast_list = get_forecast(location)

    city = current.get("name", location)
    temp = round(current["main"]["temp"])
    humidity = current["main"]["humidity"]
    condition = current["weather"][0]["description"].capitalize()

    rain_expected = any(
        "rain" in slot.get("weather", [{}])[0].get("description", "").lower()
        for slot in forecast_list
    )
    forecast_summary = "Rain expected in next 24h." if rain_expected else "No rain in next 24h."

    return {
        "location": city,
        "temperature": temp,
        "condition": condition,
        "humidity": humidity,
        "forecast_summary": forecast_summary,
    }

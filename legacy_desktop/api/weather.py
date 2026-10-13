"""
weather.py
-----------
Fetches current weather information using the OpenWeatherMap API.
"""

import os
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherService:
    """Client for retrieving current weather data for a given city."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")

    def get_weather(self, city: str, units: str = "metric") -> str:
        """
        Retrieve a human-readable weather summary for the given city.

        Args:
            city (str): City name, e.g. "Delhi".
            units (str): "metric" for Celsius, "imperial" for Fahrenheit.

        Returns:
            str: A spoken-friendly weather summary or an error message.
        """
        if not self.api_key:
            return "Weather service is not configured. Please add an OpenWeather API key."

        params = {"q": city, "appid": self.api_key, "units": units}

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            unit_symbol = "°C" if units == "metric" else "°F"

            return (
                f"The weather in {city} is currently {description} with a "
                f"temperature of {temp}{unit_symbol}, feeling like {feels_like}{unit_symbol}. "
                f"Humidity is at {humidity} percent."
            )

        except requests.exceptions.HTTPError:
            logger.warning(f"Weather API returned an error for city: {city}")
            return f"I couldn't find weather data for {city}. Please check the city name."
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return "Sorry, I couldn't connect to the weather service right now."

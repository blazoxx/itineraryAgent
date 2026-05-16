import os
import requests
import logging

from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv(
    "WEATHER_API_KEY"
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), retry=retry_if_exception_type(Exception))
def get_weather_data(
    city: str
):
    """Get weather data from OpenWeatherMap with retries/backoff on failures.

    The function is synchronous and deliberately retries transient errors.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    logger.debug("Fetching weather for %s", city)

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()
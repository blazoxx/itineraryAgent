import os
import requests

from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv(
    "WEATHER_API_KEY"
)


def get_weather_data(
    city: str
):

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params
    )

    return response.json()
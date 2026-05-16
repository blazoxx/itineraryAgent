# class WeatherAgent:

#     async def get_weather(
#         self,
#         destination: str
#     ):
#         pass

#! Dummy implementation for testing purposes
# class WeatherAgent:

#     async def get_weather(
#         self,
#         destination: str
#     ):

#         return {
#             "temperature": "30C",
#             "condition": "Sunny"
#         }
        
#! Real implementation using the weather service
from services.weather_service import (
    get_weather_data
)


class WeatherAgent:

    async def get_weather(
        self,
        destination: str
    ):

        weather_data = get_weather_data(
            destination
        )

        return {
            "temperature": weather_data[
                "main"
            ]["temp"],

            "condition": weather_data[
                "weather"
            ][0]["description"],

            "humidity": weather_data[
                "main"
            ]["humidity"]
        }
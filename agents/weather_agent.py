# class WeatherAgent:

#     async def get_weather(
#         self,
#         destination: str
#     ):
#         pass

#! Dummy implementation for testing purposes
class WeatherAgent:

    async def get_weather(
        self,
        destination: str
    ):

        return {
            "temperature": "30C",
            "condition": "Sunny"
        }
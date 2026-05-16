import pytest

from agents.weather_agent import WeatherAgent
import agents.weather_agent as weather_mod


@pytest.mark.asyncio
async def test_weather_agent_transforms(monkeypatch):
    def fake_get_weather(city):
        return {
            "main": {"temp": 26.5, "humidity": 80},
            "weather": [{"description": "light rain"}]
        }

    monkeypatch.setattr(weather_mod, "get_weather_data", fake_get_weather)

    agent = WeatherAgent()
    result = await agent.get_weather("Goa")

    assert result["temperature"] == 26.5
    assert result["condition"] == "light rain"
    assert result["humidity"] == 80

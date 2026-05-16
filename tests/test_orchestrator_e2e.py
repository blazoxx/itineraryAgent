import pytest

from orchestrator.travel_orchestrator import TravelOrchestrator
import agents.intent_agent as intent_mod
import agents.research_agent as research_mod
import agents.itinerary_agent as itin_mod
import agents.budget_agent as budget_mod
import agents.weather_agent as weather_mod


@pytest.mark.asyncio
async def test_orchestrator_end_to_end(monkeypatch):
    async def fake_intent(prompt):
        return '{"destination":"Goa","duration":3,"budget":20000,"preferences":["beaches"]}'

    async def fake_research(prompt):
        return '{"weather":"Tropical","attractions":["Baga Beach"],"best_time_to_visit":"Nov-Feb","local_transport":["scooters"]}'

    async def fake_itin(prompt):
        return '{"days":{"Day 1":["Arrive","Beach"],"Day 2":["Sightseeing"]}}'

    async def fake_budget(prompt):
        return '{"hotel":6000,"food":3000,"transport":2000,"flights":0,"activities":1000,"total":12000}'

    def fake_weather(city):
        return {"main": {"temp": 27.0, "humidity": 85}, "weather": [{"description": "clear sky"}]}

    # Patch agent-level imports
    monkeypatch.setattr(intent_mod, "ask_llm", fake_intent)
    monkeypatch.setattr(research_mod, "ask_llm", fake_research)
    monkeypatch.setattr(itin_mod, "ask_llm", fake_itin)
    monkeypatch.setattr(budget_mod, "ask_llm", fake_budget)
    monkeypatch.setattr(weather_mod, "get_weather_data", fake_weather)

    orchestrator = TravelOrchestrator()
    result = await orchestrator.execute("plan a 3 day trip to goa focused on beaches")

    assert "intent" in result
    assert "research" in result
    assert "itinerary" in result
    assert "budget" in result
    assert "weather" in result

    # Basic content checks
    assert result["intent"].destination == "Goa"
    assert result["budget"].total == 12000
    assert result["weather"]["temperature"] == 27.0

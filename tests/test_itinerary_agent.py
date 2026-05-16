import pytest

from agents.itinerary_agent import ItineraryAgent
import agents.itinerary_agent as itin_mod


@pytest.mark.asyncio
async def test_itinerary_agent_parses(monkeypatch):
    async def fake_ask(prompt):
        return '{"days": {"Day 1": ["Arrive","Relax at beach"], "Day 2": ["Sightseeing","Nightlife"]}}'

    monkeypatch.setattr(itin_mod, "ask_llm", fake_ask)

    agent = ItineraryAgent()
    class Intent: destination = "Goa"; duration = 2; budget = 20000; preferences = ["beaches"]
    class Research: attractions = ["Baga"]

    result = await agent.generate(Intent, Research)

    assert isinstance(result.days, dict)
    assert "Day 1" in result.days

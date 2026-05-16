import pytest

from agents.research_agent import ResearchAgent
import agents.research_agent as research_mod


@pytest.mark.asyncio
async def test_research_agent_parses(monkeypatch):
    async def fake_ask(prompt):
        return '{"weather":"Tropical; warm and humid","attractions":["Baga Beach","Anjuna"],"best_time_to_visit":"November to February","local_transport":["taxis","scooters"]}'

    monkeypatch.setattr(research_mod, "ask_llm", fake_ask)

    agent = ResearchAgent()
    class Intent: destination = "Goa"; preferences = ["beaches"]

    result = await agent.research(Intent)

    assert "weather" in result.__dict__
    assert "attractions" in result.__dict__

import pytest

from agents.intent_agent import IntentAgent
import agents.intent_agent as intent_mod


@pytest.mark.asyncio
async def test_intent_agent_parses(monkeypatch):
    async def fake_ask(prompt):
        return '{"destination":"Goa","duration":5,"budget":20000,"preferences":["beaches","nightlife"]}'

    monkeypatch.setattr(intent_mod, "ask_llm", fake_ask)

    agent = IntentAgent()
    result = await agent.analyze("plan a trip to goa focused on beaches and nightlife")

    assert result.destination == "Goa"
    assert result.duration == 5
    assert result.budget == 20000
    assert "beaches" in result.preferences

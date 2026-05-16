import pytest

from agents.budget_agent import BudgetAgent
import agents.budget_agent as budget_mod


@pytest.mark.asyncio
async def test_budget_agent_parses(monkeypatch):
    async def fake_ask(prompt):
        return '{"hotel":7000,"food":3000,"transport":2000,"flights":0,"activities":2000,"total":14000}'

    monkeypatch.setattr(budget_mod, "ask_llm", fake_ask)

    agent = BudgetAgent()
    class Intent: destination = "Goa"; duration = 2; budget = 20000; preferences = ["beaches"]
    compact_itin = "Day 1: beach; Day 2: sightseeing"

    result = await agent.estimate(Intent, compact_itin)

    assert result.total == 14000
    assert result.hotel == 7000

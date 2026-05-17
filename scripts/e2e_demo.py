import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.travel_orchestrator import TravelOrchestrator

USE_MOCKS = True


async def main():
    orchestrator = TravelOrchestrator()

    if USE_MOCKS:
        import agents.intent_agent as intent_mod
        import agents.research_agent as research_mod
        import agents.itinerary_agent as itin_mod
        import agents.budget_agent as budget_mod
        import agents.weather_agent as weather_mod

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

        intent_mod.ask_llm = fake_intent
        research_mod.ask_llm = fake_research
        itin_mod.ask_llm = fake_itin
        budget_mod.ask_llm = fake_budget
        weather_mod.get_weather_data = fake_weather

    result = await orchestrator.execute("plan a 3 day trip to goa focused on beaches and nightlife")

    def serialize(obj):
        try:
            return obj.model_dump()
        except Exception:
            return obj

    out = {k: (serialize(v) if k in ("intent", "research", "itinerary", "budget") else v) for k, v in result.items()}

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

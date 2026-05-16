import asyncio
import json
import sys
import os

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from orchestrator.travel_orchestrator import TravelOrchestrator
import services.llm_service as llm_service
import services.weather_service as weather_service


async def fake_ask_llm(prompt: str):
    # crude routing based on agent type in prompt
    p = prompt.lower()
    if "intent extraction" in p or "extract travel details" in p:
        return json.dumps({
            "destination": "Goa",
            "duration": 5,
            "budget": 20000,
            "preferences": ["beaches", "nightlife"]
        })
    if "travel research agent" in p or "research the travel destination" in p:
        return json.dumps({
            "weather": "Tropical; warm and humid",
            "attractions": ["Baga Beach", "Anjuna", "Dudhsagar Falls"],
            "best_time_to_visit": "November to February",
            "local_transport": ["taxis", "scooters", "local buses"]
        })
    if "travel itinerary agent" in p or "generate a realistic day-wise" in p:
        return json.dumps({
            "days": {
                "Day 1": ["Arrive in Goa", "Relax at Baga Beach"],
                "Day 2": ["Visit Dudhsagar Falls", "Sunset at Anjuna"]
            }
        })
    if "travel budget estimation" in p or "estimate realistic travel expenses" in p:
        return json.dumps({
            "hotel": 7000,
            "food": 3000,
            "transport": 2000,
            "flights": 0,
            "activities": 2000,
            "total": 14000
        })
    return json.dumps({})


def fake_get_weather_data(city: str):
    return {
        "main": {"temp": 29.5, "humidity": 78},
        "weather": [{"description": "clear sky"}]
    }


async def main():
    # patch services and agent imports (agents import ask_llm directly)
    llm_service.ask_llm = fake_ask_llm
    weather_service.get_weather_data = fake_get_weather_data

    # Agents import ask_llm directly; overwrite those references too
    import agents.intent_agent as intent_agent_mod
    import agents.research_agent as research_agent_mod
    import agents.itinerary_agent as itinerary_agent_mod
    import agents.budget_agent as budget_agent_mod

    intent_agent_mod.ask_llm = fake_ask_llm
    research_agent_mod.ask_llm = fake_ask_llm
    itinerary_agent_mod.ask_llm = fake_ask_llm
    budget_agent_mod.ask_llm = fake_ask_llm

    orchestrator = TravelOrchestrator()
    result = await orchestrator.execute("Plan a 5-day budget trip to Goa under ₹20,000")

    def to_serializable(o):
        if hasattr(o, "dict"):
            return to_serializable(o.dict())
        if isinstance(o, dict):
            return {k: to_serializable(v) for k, v in o.items()}
        if isinstance(o, list):
            return [to_serializable(x) for x in o]
        return o

    print(json.dumps(to_serializable(result), indent=2))


if __name__ == "__main__":
    asyncio.run(main())

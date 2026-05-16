from agents.intent_agent import IntentAgent
from agents.research_agent import ResearchAgent
from agents.itinerary_agent import ItineraryAgent
from agents.budget_agent import BudgetAgent
from agents.weather_agent import WeatherAgent


class TravelOrchestrator:

    def __init__(self):

        self.intent_agent = IntentAgent()
        self.research_agent = ResearchAgent()
        self.itinerary_agent = ItineraryAgent()
        self.budget_agent = BudgetAgent()
        self.weather_agent = WeatherAgent()

    async def execute(
        self,
        user_query: str
    ):

        print(
            "[Orchestrator] Starting workflow..."
        )

        intent_data = await self.intent_agent.analyze(
            user_query
        )

        print(
            "[Intent Agent] Completed."
        )

        research_data = await self.research_agent.research(
            intent_data
        )

        print(
            "[Research Agent] Completed."
        )

        itinerary_data = await self.itinerary_agent.generate(
            intent_data,
            research_data
        )

        print(
            "[Itinerary Agent] Completed."
        )
        
        compact_itinerary = {
            day: [
                activity[:60]
                for activity in activities[:2]
            ]
            for day, activities
            in itinerary_data.days.items()
        }

        budget_data = await self.budget_agent.estimate(
            intent_data,
            compact_itinerary
        )

        print(
            "[Budget Agent] Completed."
        )

        weather_data = await self.weather_agent.get_weather(
            intent_data.destination
        )

        print(
            "[Weather Agent] Completed."
        )

        return {
            "intent": intent_data,
            "research": research_data,
            "itinerary": itinerary_data,
            "budget": budget_data,
            "weather": weather_data
        }
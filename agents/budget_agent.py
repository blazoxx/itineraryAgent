from schemas.models import (
    BudgetData
)

from services.llm_service import (
    ask_llm
)

from config import USE_CACHE

class BudgetAgent:

    async def estimate(
        self,
        intent_data,
        compact_itinerary
    ):

        prompt = f"""
You are a Travel Budget Estimation Agent.

Estimate realistic travel expenses.

Destination:
{intent_data.destination}

Duration:
{intent_data.duration} days

User Budget:
{intent_data.budget}

Compact Itinerary:
{compact_itinerary}

Rules:
- Keep estimates realistic and practical
- Stay reasonably close to the user's budget
- It is acceptable to remain under budget
- Avoid unnecessarily exhausting the full budget
- The traveler is starting from India
- International trips must include realistic round-trip flight costs from India
- Domestic Indian trips should prioritize local transport costs
- International trips should allocate a significant portion to flights and hotels
- Hotel should usually consume 30–40% of the budget
- Food should usually consume 15–25%
- Activities should reflect the user's interests and travel style
- Adventure and nightlife trips may allocate more budget to activities
- Avoid unrealistic low transport costs
- Include:
    - hotel
    - food
    - transport
    - activities
- Return ONLY valid JSON
- All values must be integers
- Keep calculations concise and realistic
- Flights and local transport must be estimated separately
- Flights should represent major inter-city or international travel costs
- Transport should represent local commuting costs
- Do not over-explain
- Activities should realistically reflect ticket prices, nightlife, sightseeing, and entertainment costs.

Required Format:

{{
    "hotel": 7000,
    "food": 3000,
    "transport": 4000,
    "flights": 20000,
    "activities": 2000,
    "total": 36000
}}
"""

        response = ask_llm(prompt)

        # print(
        #     "\n[Budget Agent Raw Response]\n",
        #     response
        # )

        from utils.parser import (
        clean_json_response
        )

        parsed_data = clean_json_response(
            response
        )

        return BudgetData(
            **parsed_data
        )
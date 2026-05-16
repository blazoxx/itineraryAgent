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
- Keep estimates realistic
- Stay reasonably close to the user's budget
- It is acceptable to remain under budget
- Avoid unnecessarily exhausting the full budget
- Include:
    - hotel
    - food
    - transport
    - activities
- Return ONLY valid JSON
- All values must be integers
- Keep calculations concise
- Avoid unrealistic low transport costs

Required Format:

{{
    "hotel": 7000,
    "food": 3000,
    "transport": 4000,
    "activities": 2000,
    "total": 16000
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
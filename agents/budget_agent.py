# class BudgetAgent:

#     async def estimate(
#         self,
#         intent_data,
#         itinerary_data
#     ):
#         pass

#! Dummy implementation for testing purposes
# from schemas.models import BudgetData


# class BudgetAgent:

#     async def estimate(
#         self,
#         intent_data,
#         itinerary_data
#     ):

#         return BudgetData(
#             hotel=7000,
#             food=3000,
#             transport=4000,
#             activities=2000,
#             total=16000
#         )
        
        
#! Real Implementation
import json

from schemas.models import (
    BudgetData
)

from services.llm_service import (
    ask_llm
)


class BudgetAgent:

    async def estimate(
        self,
        intent_data,
        itinerary_data
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

Itinerary:
{itinerary_data.days}

Rules:
- Keep estimates realistic
- Stay near the user's budget
- Include:
    - hotel
    - food
    - transport
    - activities
- Return ONLY valid JSON
- All values must be integers

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

        print(
            "\n[Budget Agent Raw Response]\n",
            response
        )

        cleaned_response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed_data = json.loads(
            cleaned_response
        )

        return BudgetData(
            **parsed_data
        )
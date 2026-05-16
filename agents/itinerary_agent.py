# class ItineraryAgent:

#     async def generate(
#         self,
#         intent_data,
#         research_data
#     ):
#         pass


#! Dummy implementation for testing purposes
# from schemas.models import ItineraryData


# class ItineraryAgent:

#     async def generate(
#         self,
#         intent_data,
#         research_data
#     ):

#         return ItineraryData(
#             days={
#                 "Day 1": [
#                     "Arrival",
#                     "Beach visit"
#                 ],
#                 "Day 2": [
#                     "Fort Aguada",
#                     "Night market"
#                 ]
#             }
#         )
        
#! Real Implementation

import json

from schemas.models import (
    ItineraryData
)

from services.llm_service import (
    ask_llm
)


class ItineraryAgent:

    async def generate(
        self,
        intent_data,
        research_data
    ):

        prompt = f"""
You are an AI Travel Itinerary Agent.

Generate a realistic day-wise travel itinerary.

Destination:
{intent_data.destination}

Duration:
{intent_data.duration} days

Budget:
{intent_data.budget}

User Preferences:
{intent_data.preferences}

Top Attractions:
{research_data.attractions}

Rules:
- Create realistic schedules
- Group nearby attractions logically
- Avoid impossible timings
- Match user interests
- Keep itinerary budget-friendly

Return ONLY valid JSON.

Keep each activity short and concise.
Maximum 1 sentence per activity.
Avoid long descriptions.

Required Format:

{{
    "days": {{
        "Day 1": [
            "Activity 1",
            "Activity 2"
        ],
        "Day 2": [
            "Activity 1",
            "Activity 2"
        ]
    }}
}}
"""

        response = ask_llm(prompt)

        print(
            "\n[Itinerary Agent Raw Response]\n",
            response
        )

        from utils.parser import (
        clean_json_response
        )

        parsed_data = clean_json_response(
            response
        )

        return ItineraryData(
            **parsed_data
        )
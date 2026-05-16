# class ResearchAgent:

#     async def research(self, intent_data):
#         pass

#! Dummy implementation for testing purposes
# from schemas.models import ResearchData

# class ResearchAgent:

#     async def research(
#         self,
#         intent_data
#     ):

#         return ResearchData(
#             weather="Warm and humid",
#             attractions=[
#                 "Baga Beach",
#                 "Fort Aguada"
#             ],
#             best_time_to_visit="November to February",
#             local_transport=[
#                 "Scooter",
#                 "Taxi"
#             ]
#         )
        
#! Real Implementation

import json

from schemas.models import (
    ResearchData
)

from services.llm_service import (
    ask_llm
)


class ResearchAgent:

    async def research(
        self,
        intent_data
    ):

        prompt = f"""
You are a Travel Research Agent.

Research the destination based on the user's travel intent.

Destination:
{intent_data.destination}

Preferences:
{intent_data.preferences}

Return ONLY valid JSON.

Required Format:
{{
    "weather": "string",
    "attractions": [
        "place1",
        "place2"
    ],
    "best_time_to_visit": "string",
    "local_transport": [
        "option1",
        "option2"
    ]
}}
"""

        response = ask_llm(prompt)

        cleaned_response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed_data = json.loads(
            cleaned_response
        )

        return ResearchData(
            **parsed_data
        )
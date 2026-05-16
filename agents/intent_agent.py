# class IntentAgent:

#     async def analyze(self, user_input: str):
#         pass


#! Dummy implementation for testing purposes
# from schemas.models import IntentData

# class IntentAgent:

#     async def analyze(
#         self,
#         user_input: str
#     ):

#         return IntentData(
#             destination="Goa",
#             duration=5,
#             budget=20000,
#             preferences=[
#                 "beaches",
#                 "nightlife"
#             ]
#         )


#! Real implementation using LLM
import json

from schemas.models import IntentData
from services.llm_service import ask_llm


class IntentAgent:

    async def analyze(
        self,
        user_input: str
    ):

        prompt = f"""
You are an AI Intent Extraction Agent.

Extract travel details from the user query.

Return ONLY valid JSON.

Rules:
- duration must be integer days
- budget must be integer
- preferences must ALWAYS be a list
- infer preferences from context if possible

Example:
{{
    "destination": "Goa",
    "duration": 5,
    "budget": 20000,
    "preferences": [
        "beaches",
        "nightlife"
    ]
}}

User Query:
{user_input}
"""

        response = ask_llm(prompt)

        from utils.parser import (
        clean_json_response
)

        parsed_data = clean_json_response(
            response
        )

        return IntentData(**parsed_data)
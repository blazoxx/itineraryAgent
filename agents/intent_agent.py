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

from schemas.models import IntentData

from utils.cache import (
    save_cache,
    load_cache
)

from utils.parser import (
    clean_json_response
)

from services.llm_service import ask_llm


class IntentAgent:

    async def analyze(
        self,
        user_input: str
    ):

        cache_key = (
            user_input
            .replace(" ", "_")
            .lower()
        )

        cached = load_cache(
            cache_key
        )

        if cached:
            return IntentData(**cached)

        prompt = f"""
You are an AI Intent Extraction Agent.

Extract travel details from the user query.

Return ONLY valid JSON.

Rules:
- duration must be integer days
- budget must be integer
- preferences must ALWAYS be a list

User Query:
{user_input}
"""

        response = ask_llm(prompt)

        parsed_data = clean_json_response(
            response
        )

        save_cache(
            cache_key,
            parsed_data
        )
        
        parsed_data.setdefault(
            "budget",
            10000
        )

        parsed_data.setdefault(
            "duration",
            3
        )

        parsed_data.setdefault(
            "preferences",
            []
        )

        return IntentData(**parsed_data)
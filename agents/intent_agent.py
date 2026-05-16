from schemas.models import IntentData

from config import USE_CACHE

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


        if USE_CACHE:

            cached = load_cache(
                cache_key
            )

            if cached:

                if not cached.get("destination"):
                    cached["destination"] = (
                        "Unknown Destination"
                    )

                if not cached.get("duration"):
                    cached["duration"] = 3

                if not cached.get("budget"):
                    cached["budget"] = 50000

                if not cached.get("preferences"):
                    cached["preferences"] = []

                return IntentData(**cached)


        prompt = f"""
            You are an AI Intent Extraction Agent.

            Extract travel details from the user query.

            Return ONLY valid JSON.

            Rules:
            - duration must be integer days
            - budget must be integer
            - preferences must ALWAYS be a list
            - destination is REQUIRED
            - If duration is missing, infer a realistic default
            - If budget is missing, infer a realistic default

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


        response = await ask_llm(prompt)

        parsed_data = clean_json_response(
            response
        )


        if not parsed_data.get("destination"):

            parsed_data["destination"] = (
                "Unknown Destination"
            )

        if not parsed_data.get("duration"):

            parsed_data["duration"] = 3

        if not parsed_data.get("budget"):

            parsed_data["budget"] = 50000

        if not parsed_data.get("preferences"):

            parsed_data["preferences"] = []


        if USE_CACHE:

            save_cache(
                cache_key,
                parsed_data
            )


        return IntentData(**parsed_data)
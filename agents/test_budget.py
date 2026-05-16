#! Testing agent only

import asyncio

from agents.budget_agent import BudgetAgent
from schemas.models import (
    IntentData,
    ItineraryData
)


async def main():

    agent = BudgetAgent()

    intent = IntentData(
        destination="Goa",
        duration=5,
        budget=20000,
        preferences=[
            "beaches",
            "nightlife"
        ]
    )

    itinerary = ItineraryData(
        days={
            "Day 1": [
                "Beach visit"
            ]
        }
    )

    result = await agent.estimate(
        intent,
        itinerary
    )

    print(result)


asyncio.run(main())
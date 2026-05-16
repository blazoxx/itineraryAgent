import asyncio
from orchestrator.travel_orchestrator import (
    TravelOrchestrator
)


async def main():

    orchestrator = TravelOrchestrator()

    user_query = (
    "Plan a 5-day Goa trip under 20000 rupees "
    "focused on beaches and nightlife"
    )

    result = await orchestrator.execute(
        user_query
    )

    print("\nFINAL RESULT:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
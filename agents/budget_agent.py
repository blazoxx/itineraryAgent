# class BudgetAgent:

#     async def estimate(
#         self,
#         intent_data,
#         itinerary_data
#     ):
#         pass

#! Dummy implementation for testing purposes
from schemas.models import BudgetData


class BudgetAgent:

    async def estimate(
        self,
        intent_data,
        itinerary_data
    ):

        return BudgetData(
            hotel=7000,
            food=3000,
            transport=4000,
            activities=2000,
            total=16000
        )
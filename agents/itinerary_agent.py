# class ItineraryAgent:

#     async def generate(
#         self,
#         intent_data,
#         research_data
#     ):
#         pass


#! Dummy implementation for testing purposes

from schemas.models import ItineraryData


class ItineraryAgent:

    async def generate(
        self,
        intent_data,
        research_data
    ):

        return ItineraryData(
            days={
                "Day 1": [
                    "Arrival",
                    "Beach visit"
                ],
                "Day 2": [
                    "Fort Aguada",
                    "Night market"
                ]
            }
        )
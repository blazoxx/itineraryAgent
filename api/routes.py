from fastapi import APIRouter

from orchestrator.travel_orchestrator import (
    TravelOrchestrator
)

from schemas.models import (
    TravelRequest
)

router = APIRouter()

orchestrator = TravelOrchestrator()


@router.post("/generate-plan")
async def generate_plan(
    request: TravelRequest
):

    result = await orchestrator.execute(
        request.user_query
    )

    return result
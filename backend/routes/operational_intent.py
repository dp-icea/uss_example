from fastapi import APIRouter, Body

from uuid import UUID
from models.operational_intent import OperationalIntent
from schemas.operational_intent import CreateOperationalIntentRequest
from schemas.response import Response

router = APIRouter()

# TODO: This is provisory. I might have to change for the flight_plan api format
#   but I dont understand the area so far
@router.put(
    "/{entity_id}",
    response_description="Create a new operational intent",
    response_model=Response
)
async def create_operational_intent(
    entity_id: UUID,
    operational_intent_request: CreateOperationalIntentRequest = Body(...),
):
    """
    Create a new operational intent
    """

    operational_intent = OperationalIntent(
        entity_id=entity_id,
        volume=operational_intent_request.volume,
        time_start=operational_intent_request.time_start,
        time_end=operational_intent_request.time_end,
    )

    await operational_intent.create()

    return Response(
        status=200,
        message="Operational intent created successfully",
        data=operational_intent,
    )



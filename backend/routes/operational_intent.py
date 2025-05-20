from fastapi import APIRouter, Body, HTTPException

from uuid import UUID
from models.operational_intent import OperationalIntent
from services.auth_service import AuthService
from services.dss_service import DSSService
from schemas.operational_intent import CreateOperationalIntentRequest
from schemas.response import Response

import controllers.operational_intent as operational_intent_controller

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
    area_of_interest: CreateOperationalIntentRequest = Body(...),
):
    """
    Create a new operational intent
    """

    if await operational_intent_controller.entity_id_exists(entity_id):
        raise HTTPException(
            status_code=400,
            detail=f"Entity ID '{entity_id}' already exists",
        )

    # Verify constraints
    dss = DSSService.get_instance()
    query = await dss.query_constraint_references(area_of_interest)
    if len(query.constraint_references) != 0:
        # TODO: Send the intersection to the user later
        raise HTTPException(
            status_code=400,
            detail="Area of interest is not valid",
        )

    # Create the flight plan
    # operational_intent = OperationalIntent(
    #     entity_id=entity_id,
    #     volume=operational_intent_request.volume,
    #     time_start=operational_intent_request.time_start,
    #     time_end=operational_intent_request.time_end,
    # )
    #
    # await operational_intent.create()
    #
    # return Response(
    #     status=200,
    #     message="Operational intent created successfully",
    #     data=operational_intent,
    # )

    return Response(
        status=200,
        message="Foo",
        data={
            "foo": "bar",
        },
    )

@router.get(
    "/test",
    response_description="Just a test endpoint",
    response_model=Response
)
async def test():
    """
    Just a test endpoint
    """
        
    token = await AuthService.get_instance().get_dss_token()

    return Response(
        status=200,
        message="Test endpoint",
        data={
            "token": token,
        },
    )

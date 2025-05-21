from fastapi import APIRouter, Body, HTTPException

from uuid import UUID, uuid4
from models.operational_intent import OperationalIntentModel
from services.auth_service import AuthService
from services.dss_service import DSSService
from schemas.operational_intent import AreaOfInterestSchema
from schemas.response import Response
from schemas.error import ResponseError

import controllers.operational_intent as operational_intent_controller

router = APIRouter()

# TODO: This is provisory. I might have to change for the flight_plan api format
#   but I still dont understand how they send the area.
@router.put(
    "/",
    response_description="Create a new operational intent",
    response_model=Response,
    status_code=201,
)
async def create_operational_intent(
    area_of_interest: AreaOfInterestSchema = Body(...),
):
    """
    Create a new operational intent
    """

    # New entity id created to identify the operational intent
    entity_id = uuid4()

    # Verify constraints
    dss = DSSService.get_instance()
    query_constraints = await dss.query_constraint_references(
        area_of_interest=area_of_interest
    )
    if len(query_constraints.constraint_references) != 0:
        # TODO: Send the intersection to the user later
        raise HTTPException(
            status_code=400,
            detail=ResponseError(
                message="Area of interest is blocked by constraints.",
                data=query_constraints.model_dump(mode="json"),
            ).model_dump(mode="json"),
        )

    # Verify other Operational Intents
    query_operations = await dss.query_operational_intents(
        area_of_interest=area_of_interest,
    )
    if len(query_operations.operational_intent_references) != 0:
        raise HTTPException(
            status_code=400,
            detail=ResponseError(
                message="Area of interest is blocked by other operational intents.",
                data=query_operations.model_dump(mode="json"),
            ).model_dump(mode="json"),
        )

    # Register the operational intent reference in the DSS
    create_operation = await dss.create_operational_intent(
        entity_id=entity_id,
        area_of_interest=area_of_interest,
    )
     
    # Create the flight plan document
    operation_model = OperationalIntentModel(
        entity_id=entity_id,
        volume=area_of_interest.volume,
        time_start=area_of_interest.time_start,
        time_end=area_of_interest.time_end,
    )

    await operation_model.create()

    return Response(
        status=201,
        message="Operational intent created successfully",
        data=create_operation.model_dump(mode="json"),
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

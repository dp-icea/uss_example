from fastapi import APIRouter, Body, HTTPException
from typing import List
from uuid import uuid4
from http import HTTPStatus
from models.operational_intent import OperationalIntentModel, OperationalIntentDetails
from services.dss_service import DSSService
from services.uss_service import USSService
from schemas.area_of_interest import AreaOfInterestSchema
from schemas.response import Response
from schemas.error import ResponseError

router = APIRouter()

# TODO: This is provisory. I might have to change for the flight_plan api format
#   but I still dont understand how they send the area.
@router.put(
    "/",
    response_description="Create a new flight plan",
    response_model=Response,
    status_code=HTTPStatus.CREATED.value,
)
async def create_flight_plan(
    area_of_interest: AreaOfInterestSchema = Body(...),
):
    """
    Create a new operational intent
    """

    # New entity id created to identify the operational intent
    entity_id = uuid4()

    # Verify constraints
    dss = DSSService()
    query_constraints = await dss.query_constraint_references(
        area_of_interest=area_of_interest
    )
    if len(query_constraints.constraint_references) != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST.value,
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
            status_code=HTTPStatus.BAD_REQUEST.value,
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
     
    operation_model = OperationalIntentModel(
            reference = create_operation.operational_intent_reference,
            details = OperationalIntentDetails(
                volumes=[area_of_interest],
                off_nominal_volumes=[],
                priority=0,
            ),
    )

    await operation_model.create()

    return Response(
        status=HTTPStatus.CREATED.value,
        message="Operational intent created successfully",
        data=create_operation.model_dump(mode="json"),
    )

@router.put(
    "/with_conflict",
    response_description="Create a new flight plan with area conflicts",
    response_model=Response,
    status_code=HTTPStatus.CREATED.value,
)
async def create_flight_plan_with_conflict(
    area_of_interest: AreaOfInterestSchema = Body(...),
):
    """
    Create a new operational intent
    """

    # New entity id created to identify the operational intent
    entity_id = uuid4()

    # List of conflict ovns to be considered when creating the area with conflicts
    keys: List[str] = []

    # Verify constraints
    dss = DSSService()
    query_constraints = await dss.query_constraint_references(
        area_of_interest=area_of_interest
    )
    if len(query_constraints.constraint_references) != 0:
        for constraint in query_constraints.constraint_references:
            uss = USSService(base_url=constraint.uss_base_url, manager=constraint.manager)
            original_constraint = await uss.query_operational_intent(
                entity_id=constraint.id,
            )
            keys.append(original_constraint.reference.ovn)

    # Verify other Operational Intents
    query_operations = await dss.query_operational_intents(
        area_of_interest=area_of_interest,
    )
    if len(query_operations.operational_intent_references) != 0:
        for operation in query_operations.operational_intent_references:
            uss = USSService(base_url=operation.uss_base_url, manager=operation.manager)
            original_operation = await uss.query_operational_intent(
                entity_id=operation.id,
            )
            keys.append(original_operation.reference.ovn)

    # Register the operational intent reference in the DSS
    create_operation = await dss.create_operational_intent(
        entity_id=entity_id,
        area_of_interest=area_of_interest,
        keys=keys,
    )
     
    operation_model = OperationalIntentModel(
            reference = create_operation.operational_intent_reference,
            details = OperationalIntentDetails(
                volumes=[area_of_interest],
                off_nominal_volumes=[],
                priority=0,
            ),
    )

    await operation_model.create()

    return Response(
        status=HTTPStatus.CREATED.value,
        message="Operational intent created successfully",
        data=create_operation.model_dump(mode="json"),
    )

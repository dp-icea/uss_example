from fastapi import APIRouter, Body, HTTPException
from typing import List
from uuid import uuid4, UUID
from http import HTTPStatus

from controllers import operational_intent as operational_intent_controller
from models.operational_intent import OperationalIntentModel
from services.dss_service import DSSService
from services.uss_service import USSService
from schema_types.operational_intent import OperationalIntentState
from schema_types.ovn import ovn
from schemas.operational_intent import OperationalIntentDetailSchema, OperationalIntentSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schemas.response import Response
from schemas.error import ResponseError

async def get_obstacles_ovns(area_of_interest: AreaOfInterestSchema) -> List[ovn]:
    """
    Get the keys of obstacles in the area of interest.
    This is a placeholder function and should be implemented based on actual requirements.
    """
    # List of conflict ovns to be considered when creating the area with conflicts
    keys: List[ovn] = []

    # Verify constraints
    dss = DSSService()
    constraint_references = await dss.query_constraint_references(
        area_of_interest=area_of_interest
    )
    if len(constraint_references.constraint_references) != 0:
        for constraint in constraint_references.constraint_references:
            uss = USSService(base_url=constraint.uss_base_url, manager=constraint.manager)
            original_constraint = await uss.query_operational_intent(
                entity_id=constraint.id,
            )
            keys.append(original_constraint.operational_intent.reference.ovn)

    # Verify other Operational Intents
    query_operations = await dss.query_operational_intent_references(
        area_of_interest=area_of_interest,
    )
    if len(query_operations.operational_intent_references) != 0:
        for operation in query_operations.operational_intent_references:
            uss = USSService(base_url=operation.uss_base_url, manager=operation.manager)
            original_operation = await uss.query_operational_intent(
                entity_id=operation.id,
            )
            keys.append(original_operation.operational_intent.reference.ovn)

    return keys

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
    query_operations = await dss.query_operational_intent_references(
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
            details = OperationalIntentDetailSchema(
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
    ovns: List[ovn] = await get_obstacles_ovns(area_of_interest)

    # Register the operational intent reference in the DSS
    dss = DSSService()
    create_operation = await dss.create_operational_intent(
        entity_id=entity_id,
        area_of_interest=area_of_interest,
        keys=ovns,
    )
     
    operation_model = OperationalIntentModel(
            reference = create_operation.operational_intent_reference,
            details = OperationalIntentDetailSchema(
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

@router.patch(
    "/{entity_id}",
    response_description="Activate the flight plan",
    response_model=Response,
    status_code=HTTPStatus.OK.value,
)
async def activate_flight_plan(
    entity_id: UUID,
):
    """
    Activate the flight plan
    """

    old_operational_intent_model = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    old_operational_intent = OperationalIntentSchema(
        reference=old_operational_intent_model.reference,
        details=old_operational_intent_model.details,
    )

    old_operational_intent.reference.state = OperationalIntentState.ACTIVATED

    # TODO: Verify operational intent references in the area
    # Need to inform the keys in the update operation

    ovns: List[ovn] = []

    for area_of_interest in old_operational_intent.details.volumes:
        if area_of_interest.volume is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST.value,
                detail=ResponseError(
                    message="Flight plan has invalid operation volume volume",
                    data=area_of_interest.model_dump(mode="json"),
                ).model_dump(mode="json"),
            )
        ovns += await get_obstacles_ovns(area_of_interest)

    dss = DSSService()
    operational_intent_updated = await dss.update_operational_intent_reference(
        entity_id=entity_id,
        ovn=old_operational_intent.reference.ovn,
        keys=ovns,
        operational_intent=old_operational_intent
    )

    old_operational_intent.reference.ovn = operational_intent_updated.operational_intent_reference.ovn

    operational_intent = await operational_intent_controller.update_operational_intent(
        entity_id=entity_id,
        operational_intent=old_operational_intent,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Operational intent activated successfully",
        data=operational_intent.model_dump(mode="json"),
    )

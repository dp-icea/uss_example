from fastapi import APIRouter, Body, HTTPException
from typing import List
from uuid import uuid4, UUID
from http import HTTPStatus

from controllers import operational_intent as operational_intent_controller
from models.operational_intent import OperationalIntentModel
from services.dss_service import DSSService
from schema_types.operational_intent import OperationalIntentState
from schema_types.ovn import OVN
from schemas.operational_intent import OperationalIntentDetailSchema, OperationalIntentSchema
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
    conflicting_constraints = query_constraints.constraint_references

    # Verify other Operational Intents
    query_operations = await dss.query_operational_intent_references(
        area_of_interest=area_of_interest,
    )
    conflicting_operations = query_operations.operational_intent_references

    if conflicting_constraints or conflicting_operations:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail=ResponseError(
                message="Flight plan area of interest conflicts with existing constraints or operational intents",
                data={
                    "constraints": [constraint.model_dump(mode="json") for constraint in conflicting_constraints],
                    "operational_intents": [operation.model_dump(mode="json") for operation in conflicting_operations],
                },
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

    await operational_intent_controller.create_operational_intent(
        operational_intent=operation_model,
    )

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
    ovns: List[OVN] = await operational_intent_controller.get_close_ovns([area_of_interest])

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

@router.post(
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
    ovns: List[OVN] = []

    for area_of_interest in old_operational_intent.details.volumes:
        if area_of_interest.volume is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST.value,
                detail=ResponseError(
                    message="Flight plan has invalid operation volume volume",
                    data=area_of_interest.model_dump(mode="json"),
                ).model_dump(mode="json"),
            )
        ovns += await operational_intent_controller.get_close_ovns([area_of_interest])

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

@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified flight plan details",
    response_model=Response,
    status_code=HTTPStatus.OK.value,
)
async def get_flight_plan(
    entity_id: UUID,
):
    """
    Retrieve the specified flight plan details
    """
    
    operational_intent = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Operational intent retrieved successfully",
        data=operational_intent.model_dump(mode="json"),
    )

@router.delete(
    "/{entity_id}",
    response_description="Delete the flight plan",
    response_model=Response,
    status_code=HTTPStatus.OK.value,
)
async def delete_flight_plan(
    entity_id: UUID,
):
    """
    Delete the flight plan
    """

    dss = DSSService()

    operational_intent = await operational_intent_controller.get_operational_intent(
            entity_id=entity_id,
        )

    # TODO: Notify the subscribers from the deleted operation area
    _ = await dss.delete_operational_intent_reference(
        entity_id=operational_intent.reference.id,
        ovn=operational_intent.reference.ovn,
    )

    operational_intent_deleted = await operational_intent_controller.delete_operational_intent(
        entity_id=operational_intent.reference.id,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Operational intent deleted successfully",
        data = operational_intent_deleted.model_dump(mode="json"),
    )


@router.patch(
    "/",
    response_description="Update the flight plan",
    status_code=HTTPStatus.OK.value,
)
async def update_flight_plan(
    updated_operational_intent: OperationalIntentSchema = Body(...),
):
    dss = DSSService()

    operational_intent_reference_updated = await dss.update_operational_intent_reference(
        entity_id=updated_operational_intent.reference.id,
        ovn=updated_operational_intent.reference.ovn,
        keys=[],
        operational_intent=updated_operational_intent,
    )

    updated_operational_intent.reference = operational_intent_reference_updated.operational_intent_reference

    await operational_intent_controller.update_operational_intent(
        entity_id=updated_operational_intent.reference.id,
        operational_intent=updated_operational_intent,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Operational intent updated successfully",
        data=updated_operational_intent.model_dump(mode="json"),
    )

@router.patch(
    "/with_conflict",
    response_description="Update the flight plan with area conflicts",
    status_code=HTTPStatus.OK.value,
)
async def update_flight_plan_with_conflict(
    updated_operational_intent: OperationalIntentSchema = Body(...),
):
    ovns = await operational_intent_controller.get_close_ovns(updated_operational_intent.details.volumes)

    dss = DSSService()

    operational_intent_reference_updated = await dss.update_operational_intent_reference(
        entity_id=updated_operational_intent.reference.id,
        ovn=updated_operational_intent.reference.ovn,
        keys=ovns,
        operational_intent=updated_operational_intent,
    )

    updated_operational_intent.reference = operational_intent_reference_updated.operational_intent_reference

    await operational_intent_controller.update_operational_intent(
        entity_id=updated_operational_intent.reference.id,
        operational_intent=updated_operational_intent,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Operational intent updated successfully",
        data=updated_operational_intent.model_dump(mode="json"),
    )


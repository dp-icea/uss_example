from http import HTTPStatus
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, HTTPException

from config.logger import OperatorInputLogger, log_route_handler
from models.constraint import ConstraintModel
from schemas.response import Response
from schemas.constraint import ConstraintDetailSchema, ConstraintSchema
from schemas.area_of_interest import AreaOfInterestSchema
from controllers import constraint as constraint_controller
from services.dss_service import DSSService

router = APIRouter()

DEFAULT_CONSTRAINT_TYPE = "uss.icea.non_utm_aircraft_operations"

@router.put(
    "/",
    response_description="Add a new constraint",
    status_code=HTTPStatus.CREATED.value,
)
@log_route_handler(OperatorInputLogger, "Constraint Added")
async def add_constraint(
    areas_of_interest: List[AreaOfInterestSchema]
):

    entity_id = uuid4()

    dss = DSSService()
    constraint_created = await dss.create_constraint_reference(
        entity_id=entity_id,
        areas_of_interest=areas_of_interest,
    )

    constraint = ConstraintSchema(
        reference=constraint_created.constraint_reference,
        details= ConstraintDetailSchema(
            volumes=areas_of_interest,
            type=DEFAULT_CONSTRAINT_TYPE,
            geozone=None,
        ),
    )

    await constraint_controller.create_constraint(
        constraint_model=ConstraintModel(
            constraint=constraint,
        )
    )

    await constraint_controller.notify_subscribers(
        subscribers=constraint_created.subscribers,
        constraint_id=entity_id,
        constraint=constraint,
    )

    return Response(
        status=HTTPStatus.CREATED.value,
        message="Constraint created successfully.",
        data=constraint_created.model_dump(mode="json"),
    )

@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified constraint details",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
@log_route_handler(OperatorInputLogger, "Constraint Retrieved")
async def get_constraint(
    entity_id: UUID,
):
    """
    Retrieve the specified constraint details.
    """
    # Verify if the Constraint exists
    constraint_model = await constraint_controller.get_constraint(entity_id=entity_id)

    if constraint_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    return {
        "constraint": constraint_model.constraint.model_dump(mode="json"),
    }

@router.delete(
    "/{entity_id}",
    response_description="Delete a constraint",
    status_code=HTTPStatus.NO_CONTENT.value,
)
@log_route_handler(OperatorInputLogger, "Constraint Deleted")
async def delete_constraint(
    entity_id: UUID,
):
    """
    Delete a constraint by its entity ID.
    """
    dss = DSSService()

    # Verify if the Constraint exists
    constraint = await constraint_controller.get_constraint(entity_id=entity_id)

    # Delete the constraint reference in the DSS
    constraint_reference_deleted = await dss.delete_constraint_reference(
        entity_id=constraint.reference.id,
        ovn=constraint.reference.ovn,
    )

    # Delete the constraint in the USS database
    await constraint_controller.delete_constraint(entity_id=entity_id)

    await constraint_controller.notify_subscribers(
        subscribers=constraint_reference_deleted.subscribers,
        constraint_id=entity_id,
        constraint=None,
    )

@router.patch(
    "/",
    response_description="Update a constraint",
    status_code=HTTPStatus.OK.value,
)
@log_route_handler(OperatorInputLogger, "Constraint Updated")
async def update_constraint(
    new_constraint: ConstraintSchema,
):
    """
    Update an existing constraint by its entity ID.
    """
    dss = DSSService()

    # Update the constraint reference in the DSS
    constraint_reference_updated = await dss.update_constraint_reference(
        entity_id=new_constraint.reference.id,
        ovn=new_constraint.reference.ovn,
        constraint=new_constraint,
    )

    new_constraint.reference = constraint_reference_updated.constraint_reference

    # Update the modified constraint values in the USS database
    updated_constraint = await constraint_controller.update_constraint(
        entity_id=new_constraint.reference.id,
        new_constraint=new_constraint,
    )

    # Notify subscribers about the updated constraint
    await constraint_controller.notify_subscribers(
        subscribers=constraint_reference_updated.subscribers,
        constraint_id=new_constraint.reference.id,
        constraint=new_constraint,
    )

    return Response(
        status=HTTPStatus.OK.value,
        message="Constraint updated successfully.",
        data=updated_constraint.model_dump(mode="json"),
    )

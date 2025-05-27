from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException

from controllers import constraint as constraint_controller
from schemas.constraint import ConstraintNotificationRequest
from services.dss_service import DSSService
from schema_types.constraint import ConstraintState

router = APIRouter()

@router.post(
    "/",
    response_description="Receive notification of changed constraints",
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def handle_constraint_notification(
    notification: ConstraintNotificationRequest,
):
    # Verify if the Constraint should be deleted
    if notification.constraint is None:
        constraint = await constraint_controller.get_constraint(
            entity_id=notification.constraint_id,
        )
        
        # Delete the constraint from the DSS database
        dss = DSSService()
        _ = await dss.delete_constraint_reference(
            entity_id=constraint.reference.id,
            ovn=constraint.reference.ovn,
        )

        await constraint_controller.delete_constraint(
            entity_id=constraint.reference.id,
        )

        return

    # Update the modified constraint values in the USS database
    await constraint_controller.update_constraint(
        entity_id=notification.constraint_id,
        new_constraint=notification.constraint,
    )

@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified constraint details",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
async def get_constraint(entity_id: UUID):
    constraint = await constraint_controller.get_constraint(entity_id)

    if constraint is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    return {
            "constraint": constraint.model_dump(mode="json"),
    }

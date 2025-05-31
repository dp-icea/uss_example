from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException

from config.logger import MessageLogger
from controllers import constraint as constraint_controller
from schemas.constraint import ConstraintNotificationRequest
from services.dss_service import DSSService
from schema_types.constraint import ConstraintState

router = APIRouter()

# TODO: In the future. Implement a webhook for the client to receive constant updates
@router.post(
    "/",
    response_description="Receive notification of new constraints in the area",
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def handle_constraint_notification(
    notification: ConstraintNotificationRequest,
): 
    """
    Receive notification of new constraints in the area
    """

    if notification.constraint is None:
        # If the constraint is not provided, we cannot process the notification
        MessageLogger.log(
            f"Constraint removed",
            data=notification.model_dump(mode="json"),
        )
        return

    # Log the received notification
    MessageLogger.log(
        f"Constraint changed",
        data=notification.model_dump(mode="json"),
    )

@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified constraint details",
    response_model=dict,
    status_code=HTTPStatus.OK.value,
)
async def get_constraint(entity_id: UUID):
    constraint_model = await constraint_controller.get_constraint(entity_id)

    if constraint_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    return {
            "constraint": constraint_model.constraint.model_dump(mode="json"),
    }

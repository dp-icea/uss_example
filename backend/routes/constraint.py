from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException

from controllers import constraint as constraint_controller

router = APIRouter()

@router.post(
    "/",
    response_description="Receive notification of changed constraints",
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def handle_constraint_notification():
    raise HTTPException(
        status_code=HTTPStatus.NOT_IMPLEMENTED.value,
        detail="Constraint notification handling is not implemented yet."
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

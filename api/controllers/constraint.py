from fastapi import HTTPException
from http import HTTPStatus
from uuid import UUID
from typing import List, Optional

from models.constraint import ConstraintModel
from services.dss_service import DSSService
from services.uss_service import USSService
from schemas.constraint import ConstraintSchema
from schema_types.subscription import SubscriberSchema, SubscriptionBaseSchema

async def get_constraint(entity_id: UUID) -> ConstraintModel:
    """
    Retrieve the specified operational intent details
    """
    constraint = await ConstraintModel.find_one({
        "constraint.reference.id": entity_id
    })

    if constraint is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    return constraint

async def create_constraint(constraint_model: ConstraintModel) -> ConstraintModel:
    """
    Create a new constraint in the USS database.
    """
    existing_constraint = await ConstraintModel.find_one({
        "constraint.reference.id": constraint_model.constraint.reference.id
    })

    if existing_constraint:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail="Constraint already exists in the USS database"
        )

    return await constraint_model.save()

async def delete_constraint(entity_id: UUID) -> None:
    """
    Delete a constraint from the USS database.
    """
    constraint_model = await get_constraint(entity_id)

    if constraint_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    await constraint_model.delete()

async def update_constraint(entity_id: UUID, new_constraint: ConstraintSchema) -> ConstraintModel:
    """
    Update an existing constraint in the USS database.
    """
    constraint_model = await get_constraint(entity_id)

    if constraint_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    constraint_model.constraint = new_constraint

    return await constraint_model.save()
    
async def notify_subscribers(
        subscribers: List[SubscriberSchema],
        constraint_id: UUID,
        constraint: Optional[ConstraintSchema],

):
    for subscriber in subscribers:
        uss = USSService(base_url=subscriber.uss_base_url)
        await uss.notify_constraint(
            subscriptions=subscriber.subscriptions,
            constraint_id=constraint_id,
            constraint=constraint,
        )

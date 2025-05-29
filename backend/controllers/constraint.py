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

async def create_constraint(constraint: ConstraintModel) -> ConstraintModel:
    """
    Create a new constraint in the USS database.
    """
    existing_constraint = await ConstraintModel.find_one({
        "constraint.reference.id": constraint.reference.id
    })

    if existing_constraint:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail="Constraint already exists in the USS database"
        )

    await constraint.save()

    return constraint

async def delete_constraint(entity_id: UUID) -> None:
    """
    Delete a constraint from the USS database.
    """
    constraint = await get_constraint(entity_id)

    if constraint is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    await constraint.delete()

async def update_constraint(entity_id: UUID, new_constraint: ConstraintSchema) -> ConstraintModel:
    """
    Update an existing constraint in the USS database.
    """
    constraint = await get_constraint(entity_id)

    if constraint is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Constraint not found in the USS database"
        )

    constraint.constraint = new_constraint

    return await constraint.save()
    
async def notify_subscribers(
        subscribers: List[SubscriberSchema],
        constraint_id: UUID,
        constraint: Optional[ConstraintSchema],

):
    dss = DSSService()
    for subscription in subscribers:
        subscription_response = await dss.get_subscription(subscription_id=subscription.subscription_id)
        uss = USSService(base_url=subscription_response.subscription.uss_base_url)
        await uss.notify_constraint(
            subscription=subscription,
            constraint_id=constraint_id,
            constraint=constraint,
        )

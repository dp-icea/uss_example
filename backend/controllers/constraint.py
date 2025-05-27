from fastapi import HTTPException
from http import HTTPStatus
from uuid import UUID

from models.constraint import ConstraintModel

async def get_constraint(entity_id: UUID) -> ConstraintModel:
    """
    Retrieve the specified operational intent details
    """
    constraint = await ConstraintModel.find_one({
        "reference.id": entity_id
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
        "reference.id": constraint.reference.id
    })

    if existing_constraint:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail="Constraint already exists in the USS database"
        )

    await constraint.save()

    return constraint

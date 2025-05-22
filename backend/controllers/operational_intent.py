from fastapi import HTTPException
from http import HTTPStatus
from models.operational_intent import OperationalIntentModel
from uuid import UUID

async def entity_id_exists(entity_id: UUID) -> bool:
    """
    Check if the entity ID exists in the database.
    """

    return await OperationalIntentModel.find_one({
        "entity_id": entity_id
    }).exists()

async def get_operational_intent(entity_id: UUID) -> OperationalIntentModel:
    """
    Retrieve the specified operational intent details
    """
    operational_intent = await OperationalIntentModel.find_one({
        "reference.id": entity_id
    })

    if operational_intent is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Operational intent not found"
        )
    return operational_intent

async def delete_operational_intent(entity_id: UUID) -> None:
    """
    Delete the specified operational intent
    """
    operational_intent = await OperationalIntentModel.find_one({
        "reference.id": entity_id
    })

    if operational_intent is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Operational intent not found"
        )

    await operational_intent.delete()

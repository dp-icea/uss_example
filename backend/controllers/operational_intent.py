from fastapi import HTTPException
from http import HTTPStatus
from uuid import UUID

from models.operational_intent import OperationalIntentModel
from schemas.operational_intent import OperationalIntentSchema
from schema_types.operational_intent import OperationalIntentState

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

async def update_operational_intent(entity_id: UUID, operational_intent: OperationalIntentSchema) -> OperationalIntentModel:
    """
    Activate the specified operational intent
    """
    operational_intent_model = await get_operational_intent(entity_id)

    operational_intent_model.reference = operational_intent.reference
    operational_intent_model.details = operational_intent.details

    return await operational_intent_model.save()


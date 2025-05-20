from models.operational_intent import OperationalIntentModel
from uuid import UUID

async def entity_id_exists(entity_id: UUID) -> bool:
    """
    Check if the entity ID exists in the database.
    """

    return await OperationalIntentModel.find_one({
        "entity_id": entity_id
    }).exists()



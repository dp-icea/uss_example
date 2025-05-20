from models.operational_intent import OperationalIntent
from uuid import UUID

async def entity_id_exists(entity_id: UUID) -> bool:
    """
    Check if the entity ID exists in the database.
    """

    return await OperationalIntent.find_one({
        "entity_id": entity_id
    }).exists()



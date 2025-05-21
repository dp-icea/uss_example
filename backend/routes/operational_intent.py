from uuid import UUID
from fastapi import APIRouter
import controllers.operational_intent as operational_intent_controller

router = APIRouter()

@router.get(
    "/{entity_id}",
    response_description="Retrieve the specified operational intent details",
    status_code=200,
)
async def get_operational_intent(
    entity_id: UUID,
):
    """
    Retrieve the specified operational intent details
    """

    # Get the operational intent from the DSS
    operational_intent = await operational_intent_controller.get_operational_intent(
        entity_id=entity_id,
    )

    return {
        "operational_intent": operational_intent.model_dump(mode="json"),
    }

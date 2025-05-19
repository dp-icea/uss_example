from fastapi import APIRouter, Body

from models.test import Test
from models.operational_intent import OperationalIntent
from schemas.response import Response

router = APIRouter()

@router.put(
    "/{entity_id}",
    response_description="Create a new operational intent",
    reponse_model=Response
)
async def create_operational_intent(
    entity_id: str,
    operational_intent: OperationalIntent = Body(...),
):
    """
    Create a new operational intent
    """
    operational_intent = await operational_intent.create()
    return {
        "status": 200,
        "message": "Operational intent created successfully",
        "data": operational_intent,
    }

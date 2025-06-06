from typing import List, Optional
from fastapi import HTTPException
from http import HTTPStatus
from uuid import UUID

from models.operational_intent import OperationalIntentModel
from services.dss_service import DSSService
from services.uss_service import USSService
from schemas.operational_intent import OperationalIntentSchema
from schema_types.subscription import SubscriberSchema, SubscriptionBaseSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.operational_intent import OperationalIntentState
from schema_types.ovn import ovn

async def entity_id_exists(entity_id: UUID) -> bool:
    """
    Check if the entity ID exists in the database.
    """
    return await OperationalIntentModel.find_one({
        "operational_intent.reference.id": entity_id
    }).exists()

async def get_operational_intent(entity_id: UUID) -> OperationalIntentModel:
    """
    Retrieve the specified operational intent details
    """
    operational_intent_model = await OperationalIntentModel.find_one({
        "operational_intent.reference.id": entity_id
    })

    if operational_intent_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Operational intent not found"
        )
    return operational_intent_model

async def delete_operational_intent(entity_id: UUID) -> OperationalIntentModel:
    """
    Delete the specified operational intent
    """

    operational_intent_model = await OperationalIntentModel.find_one({
        "operational_intent.reference.id": entity_id
    })

    if operational_intent_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Operational intent not found"
        )

    operational_intent_model.operational_intent.reference.state = OperationalIntentState.DELETED
    return await operational_intent_model.save()

async def create_operational_intent(operational_intent_model: OperationalIntentModel) -> OperationalIntentModel:
    """
    Create a new operational intent
    """
    # New entity id created to identify the operational intent
    entity_id = operational_intent_model.operational_intent.reference.id

    if await entity_id_exists(entity_id):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail="Operational intent with this entity ID already exists"
        )

    return await operational_intent_model.save()

async def update_operational_intent(entity_id: UUID, operational_intent: OperationalIntentSchema) -> OperationalIntentModel:
    """
    Activate the specified operational intent
    """
    operational_intent_model = await get_operational_intent(entity_id)

    if operational_intent_model is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Operational intent not found"
        )

    operational_intent_model.operational_intent = operational_intent

    return await operational_intent_model.save()

async def get_close_ovns(areas_of_interest: List[AreaOfInterestSchema]) -> List[ovn]:
    """
    Get the keys of obstacles in the area of interest.
    This is a placeholder function and should be implemented based on actual requirements.
    """
    # List of conflict ovns to be considered when creating the area with conflicts
    keys: List[ovn] = []

    # Verify constraints
    dss = DSSService()
    for area_of_interest in areas_of_interest:
        constraints_queried = await dss.query_constraint_references(
            area_of_interest=area_of_interest
        )
        if len(constraints_queried.constraint_references) != 0:
            for constraint in constraints_queried.constraint_references:
                uss = USSService(base_url=constraint.uss_base_url)
                original_constraint = await uss.get_constraint(
                    entity_id=constraint.id,
                )
                keys.append(original_constraint.constraint.reference.ovn)

        # Verify other Operational Intents
        query_operations = await dss.query_operational_intent_references(
            area_of_interest=area_of_interest,
        )
        if len(query_operations.operational_intent_references) != 0:
            for operation in query_operations.operational_intent_references:
                uss = USSService(base_url=operation.uss_base_url)
                original_operation = await uss.get_operational_intent(
                    entity_id=operation.id,
                )
                keys.append(original_operation.operational_intent.reference.ovn)

    return keys

async def notify_subscribers(
        subscribers: List[SubscriberSchema],
        operational_intent_id: UUID,
        operational_intent: Optional[OperationalIntentSchema],

):
    for subscriber in subscribers:
        uss = USSService(base_url=subscriber.uss_base_url)
        await uss.notify_operational_intent(
            subscriptions=subscriber.subscriptions,
            operational_intent_id=operational_intent_id,
            operational_intent=operational_intent,
        )

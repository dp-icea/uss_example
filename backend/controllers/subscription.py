from typing import List
from fastapi import HTTPException
from http import HTTPStatus
from uuid import UUID

from models.subscription import SubscriptionModel
from services.dss_service import DSSService
from services.uss_service import USSService
from schemas.operational_intent import OperationalIntentSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.operational_intent import OperationalIntentState
from schema_types.ovn import ovn

async def create_subscription(subscription: SubscriptionModel) -> SubscriptionModel:
    """
    Create a new subscription in the database.
    """

    existing_subscription = await SubscriptionModel.find_one({
        "subscription.id": subscription.subscription.id
    })

    if existing_subscription:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT.value,
            detail="Subscription already exists"
        )

    return await subscription.save()

async def get_subscription(subscription_id: UUID) -> SubscriptionModel:
    """
    Retrieve the specified subscription details.
    """
    subscription = await SubscriptionModel.find_one({
        "subscription.id": subscription_id
    })

    if subscription is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Subscription not found"
        )

    return subscription


from http import HTTPStatus
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, HTTPException

from models.subscription import SubscriptionModel
from schemas.response import Response
from schemas.constraint import ConstraintDetailSchema
from schemas.area_of_interest import AreaOfInterestSchema
from controllers import subscription as subscription_controller
from services.dss_service import DSSService

router = APIRouter()

DEFAULT_CONSTRAINT_TYPE = "uss.icea.non_utm_aircraft_operations"

@router.put(
    "/",
    response_description="Add a new subcription",
    status_code=HTTPStatus.CREATED.value,
)
async def add_subscription(
    area_of_interest: AreaOfInterestSchema
):
    dss = DSSService()
    subscription_id = uuid4()

    # Create a new subscription in the DSS
    subscription_created = await dss.create_subscription(
        subscription_id=subscription_id,
        area_of_interest=area_of_interest,
    )
    
    subscription_model = SubscriptionModel(
        subscription=subscription_created.subscription
    )

    await subscription_controller.create_subscription(subscription_model)


    return Response(
        status=HTTPStatus.CREATED.value,
        message="Subscription created successfully.",
        data=subscription_created.model_dump(mode="json")
    )

@router.get(
    "/{subscription_id}",
    response_description="Get subscription details",
    status_code=HTTPStatus.OK.value,
)
async def get_subscription(subscription_id: UUID):
    """
    Get the details of a subscription by its ID.
    """
    subscription = await subscription_controller.get_subscription(subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Subscription not found"
        )

    return Response(
        status=HTTPStatus.OK.value,
        message="Subscription retrieved successfully.",
        data=subscription.model_dump(mode="json")
    )

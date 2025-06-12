from http import HTTPStatus
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, HTTPException

from models.subscription import SubscriptionModel
from config.logger import OperatorInputLogger, log_route_handler
from schemas.response import Response
from schemas.constraint import ConstraintDetailSchema
from schemas.area_of_interest import AreaOfInterestSchema
from controllers import subscription as subscription_controller
from services.dss_service import DSSService

router = APIRouter()

DEFAULT_CONSTRAINT_TYPE = "uss.icea.non_utm_aircraft_operations"

@router.put(
    "/",
    response_description="Add a new subscription",
    status_code=HTTPStatus.CREATED.value,
)
@log_route_handler(OperatorInputLogger, "Subscription Added")
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
@log_route_handler(OperatorInputLogger, "Subscription Retrieved")
async def get_subscription(subscription_id: UUID):
    """
    Get the details of a subscription by its ID.
    """
    dss = DSSService()

    subscription = await dss.get_subscription(subscription_id)

    return Response(
        status=HTTPStatus.OK.value,
        message="Subscription retrieved successfully.",
        data=subscription.model_dump(mode="json")
    )

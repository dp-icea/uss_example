from typing import List, Any, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, model_validator
from schemas.operational_intent import OperationalIntentReference
from schemas.area_of_interest import AreaOfInterestSchema

class OperationQueryResponse(BaseModel):
    operational_intent_references: List[OperationalIntentReference]

class OperationGetResponse(BaseModel):
    operational_intent_reference: OperationalIntentReference

class NewSubscription(BaseModel):
    uss_base_url: HttpUrl
    notify_for_constraints: bool

class OperationCreateRequest(BaseModel):
    extents: List[AreaOfInterestSchema]
    key: List[Any]
    state: str
    uss_base_url: HttpUrl
    subscription_id: Optional[UUID] = None
    new_subscription: Optional[NewSubscription] = None
    flight_type: str

    @model_validator(mode="before")
    def check_subscription_fields(cls, values):
        subscription_id = values.get('subscription_id')
        new_subscription = values.get('new_subscription')
        if (subscription_id is None and new_subscription is None) or (subscription_id is not None and new_subscription is not None):
            raise ValueError("Exactly one of 'subscription_id' or 'new_subscription' must be provided.")
        return values

class OperationCreateResponse(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReference

class OperationDeleteResponse(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReference


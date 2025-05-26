from typing import List, Any, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, model_validator

from schemas.area_of_interest import AreaOfInterestSchema
from schemas.operational_intent import OperationalIntentReferenceSchema
from schemas.subscription import NewSubscription

class OperationalIntentReferenceQueryRequest(BaseModel):
    area_of_interest: AreaOfInterestSchema

class OperationalIntentReferenceQueryResponse(BaseModel):
    operational_intent_references: List[OperationalIntentReferenceSchema]

class OperationalIntentReferenceGetResponse(BaseModel):
    operational_intent_reference: OperationalIntentReferenceSchema

class OperationalIntentReferenceCreateRequest(BaseModel):
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

class OperationalIntentReferenceCreateResponse(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReferenceSchema

class OperationalIntentReferenceUpdateRequest(BaseModel):
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

class OperationalIntentReferenceDeleteResponse(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReferenceSchema

class OperationalIntentReferenceUpdateResponse(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReferenceSchema



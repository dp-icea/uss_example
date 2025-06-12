from uuid import UUID
from typing import List
from pydantic import BaseModel, HttpUrl

from schemas.constraint import ConstraintReferenceSchema
from schemas.operational_intent import OperationalIntentReferenceSchema
from schema_types.datetime import DatetimeSchema
from schemas.area_of_interest import AreaOfInterestSchema

class SubscriptionSchema(BaseModel):
    id: UUID
    notification_index: int
    version: str
    time_start: DatetimeSchema
    time_end: DatetimeSchema
    uss_base_url: HttpUrl
    notify_for_operational_intents: bool
    notify_for_constraints: bool
    implicit_subscription: bool
    dependent_operational_intents: List[UUID]

class SubscriptionCreateRequest(BaseModel):
    extents: AreaOfInterestSchema
    uss_base_url: HttpUrl
    notify_for_constraints: bool = True
    notify_for_operational_intents: bool = True

class SubscriptionCreateResponse(BaseModel):
    subscription: SubscriptionSchema
    operational_intent_references: List[OperationalIntentReferenceSchema]
    constraint_references: List[ConstraintReferenceSchema]

class SubscriptionGetResponse(BaseModel):
    subscription: SubscriptionSchema

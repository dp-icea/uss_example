from uuid import UUID
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, HttpUrl

from schemas.time_point import TimePoint
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.subscription import SubscriptionBaseSchema
from schema_types.operational_intent import (
        OperationalIntentUSSAvailability,
        OperationalIntentState
)

class OperationalIntentDetailSchema(BaseModel):
    volumes: List[AreaOfInterestSchema]
    off_nominal_volumes: List[Any]
    priority: int

class OperationalIntentReferenceSchema(BaseModel):
    id: UUID
    flight_type: str
    manager: str
    uss_availability: OperationalIntentUSSAvailability
    version: int
    state: OperationalIntentState
    ovn: str
    time_start: TimePoint
    time_end: TimePoint
    uss_base_url: HttpUrl
    subscription_id: UUID

class OperationalIntentSchema(BaseModel):
    reference: OperationalIntentReferenceSchema
    details: OperationalIntentDetailSchema

class OperationalIntentNotificationRequest(BaseModel):
    operational_intent_id: UUID
    operational_intent: Optional[OperationalIntentSchema]
    subscriptions: List[SubscriptionBaseSchema]

class OperationalIntentGetResponse(BaseModel):
    operational_intent: OperationalIntentSchema


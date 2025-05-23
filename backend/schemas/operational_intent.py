from uuid import UUID
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, HttpUrl
from schemas.time_point import TimePoint
from schemas.area_of_interest import AreaOfInterestSchema

class OperationalIntentState(str, Enum):
    ACCEPTED = "Accepted"
    ACTIVATED = "Activated"
    NONCONFORMING = "Nonconforming"
    DELETED = "Deleted"

class OperationalIntentUSSAvailability(str, Enum):
    UNKNOWN = "Unknown"

class OperationalIntentDetails(BaseModel):
    volumes: List[AreaOfInterestSchema]
    off_nominal_volumes: List[Any]
    priority: int

class OperationalIntentReference(BaseModel):
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
    reference: OperationalIntentReference
    details: OperationalIntentDetails

    class Settings:
        name = "operational_intent"

class OperationNotificationRequest(BaseModel):
    operational_intent_id: UUID
    operational_intent: Optional[OperationalIntentSchema]
    subscriptions: List[Any]


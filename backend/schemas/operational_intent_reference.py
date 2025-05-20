from typing import List, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl
from schemas.operational_intent import TimePoint

class OperationalIntentReferenceQuery(BaseModel):
    operational_intent_references: List[Any]

class OperationalIntentReferenceDetail(BaseModel):
    id: UUID
    flight_type: str
    manager: str
    uss_availability: str
    version: int
    state: str
    ovn: str
    time_start: TimePoint
    time_end: TimePoint
    uss_base_url: str
    subscription_id: UUID

class OperationalIntentReferenceCreate(BaseModel):
    subscribers: List[Any]
    operational_intent_reference: OperationalIntentReferenceDetail


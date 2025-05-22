from uuid import UUID
from typing import Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
from schemas.operational_intent_reference import OperationalIntentReference

class TimePoint(BaseModel):
    value: datetime
    format: str

class AreaOfInterestSchema(BaseModel):
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

class OperationalIntentDetails(BaseModel):
    volumes: List[AreaOfInterestSchema]
    off_nominela_volumes: List[Any]
    priority: int

class OperationalIntentSchema(BaseModel):
    reference: OperationalIntentReference
    details: OperationalIntentDetails

    class Settings:
        name = "operational_intent"

class OperationNotificationRequest(BaseModel):
    operational_intent_id: UUID
    operational_intent: Optional[OperationalIntentSchema]
    subscriptions: List[Any]


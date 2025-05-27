from uuid import UUID
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, HttpUrl

from schemas.time_point import TimePoint
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.constraint import ConstraintUSSAvailability, ConstraintState

class ConstraintDetailSchema(BaseModel):
    volumes: List[AreaOfInterestSchema]
    # TODO: Verify those two fields later
    # I think they are not necessarly required to be informed to the DSS
    # but must be saved in the USS database
    type: str
    geozone: Any

class ConstraintReferenceSchema(BaseModel):
    id: UUID
    manager: str
    time_end: TimePoint
    time_start: TimePoint
    uss_availability: ConstraintUSSAvailability
    uss_base_url: HttpUrl
    version: int
    ovn: str

class ConstraintSchema(BaseModel):
    reference: ConstraintReferenceSchema
    details: ConstraintDetailSchema

class ConstraintNotificationRequest(BaseModel):
    constraint_id: UUID
    constraint: Optional[ConstraintSchema]
    subscriptions: List[Any]

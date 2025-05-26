from typing import List, Any
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, HttpUrl

from schemas.area_of_interest import AreaOfInterestSchema
from schemas.time_point import TimePoint
from schema_types.constraint import ConstraintUSSAvailability, ConstraintState

class ConstraintReferenceSchema(BaseModel):
    id: UUID
    flight_type: str
    manager: str
    uss_availability: ConstraintUSSAvailability
    version: int
    state: ConstraintState
    ovn: str
    time_start: TimePoint
    time_end: TimePoint
    uss_base_url: HttpUrl
    subscription_id: UUID

class ConstraintReferenceQueryRequest(BaseModel):
    area_of_interest: AreaOfInterestSchema

class ConstraintReferenceQueryResponse(BaseModel):
    # TODO: This was not tested yet. Just copied the format from the ConstraintReference
    constraint_references: List[ConstraintReferenceSchema]

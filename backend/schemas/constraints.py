from typing import List, Any
from enum import Enum
from schemas.operational_intent import TimePoint
from uuid import UUID
from schemas.operational_intent import AreaOfInterestSchema
from pydantic import BaseModel, HttpUrl

class ConstraintQueryRequest(BaseModel):
    """
    Request model for querying constraints.
    """
    area_of_interest: List[AreaOfInterestSchema]

# TODO: All those things are copied from the schemas.operational_intent_reference.py
# should change when testing with constraints
class ConstraintState(str, Enum):
    ACCEPTED = "Accepted"
    ACTIVATED = "Activated"
    NONCONFORMING = "Nonconforming"

class ConstraintUSSAvailability(str, Enum):
    UNKNOWN = "Unknown"

class ConstraintReference(BaseModel):
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

class ConstraintQueryResponse(BaseModel):
    # TODO: This was not tested yet. Just copied the format from the ConstraintReference
    constraint_references: List[ConstraintReference]


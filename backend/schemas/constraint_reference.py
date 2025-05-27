from typing import List, Any
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, HttpUrl

from schemas.area_of_interest import AreaOfInterestSchema
from schemas.time_point import TimePoint
from schemas.constraint import ConstraintReferenceSchema
from schema_types.constraint import ConstraintUSSAvailability, ConstraintState

class ConstraintReferenceQueryRequest(BaseModel):
    area_of_interest: AreaOfInterestSchema

class ConstraintReferenceQueryResponse(BaseModel):
    # TODO: This was not tested yet. Just copied the format from the ConstraintReference
    constraint_references: List[ConstraintReferenceSchema]

class ConstraintReferenceCreateRequest(BaseModel):
    extents: List[AreaOfInterestSchema]
    uss_base_url: HttpUrl

class ConstraintReferenceCreateResponse(BaseModel):
    subscribers: List[Any]
    constraint_reference: ConstraintReferenceSchema

class ConstraintReferenceDeleteResponse(BaseModel):
    subscribers: List[Any]
    constraint_reference: ConstraintReferenceSchema

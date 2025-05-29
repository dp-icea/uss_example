from uuid import UUID
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, HttpUrl

from schema_types.datetime import DatetimeSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.subscription import SubscriptionBaseSchema
from schema_types.constraint import ConstraintUSSAvailability, ConstraintState
from schema_types.availability import USSAvailability

class USSAvailabilityStatusSchema(BaseModel):
    uss: str
    availability: USSAvailability

class USSAvailabilityRequest(BaseModel):
    old_version: str = ""
    availability: USSAvailability

class USSAvailabilityResponse(BaseModel):
    version: str
    status: USSAvailabilityStatusSchema


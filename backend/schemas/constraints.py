from typing import List, Any
from schemas.operational_intent import AreaOfInterestSchema
from pydantic import BaseModel

class ConstraintQueryRequest(BaseModel):
    """
    Request model for querying constraints.
    """
    area_of_interest: List[AreaOfInterestSchema]

class ConstraintQueryResponse(BaseModel):
    constraint_references: List[Any]


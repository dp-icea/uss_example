from typing import List, Any
from pydantic import BaseModel

class ConstraintQueryResponse(BaseModel):
    constraint_references: List[Any]

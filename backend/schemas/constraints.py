from typing import List
from pydantic import BaseModel

class ConstraintReferenceQuery(BaseModel):
    constraint_references: List[str]

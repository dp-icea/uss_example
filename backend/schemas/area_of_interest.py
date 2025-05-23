from schemas.time_point import TimePoint
from pydantic import BaseModel
from typing import Any

class AreaOfInterestSchema(BaseModel):
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

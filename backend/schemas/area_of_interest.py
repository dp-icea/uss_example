from pydantic import BaseModel
from typing import Any

from schemas.time_point import TimePoint

class AreaOfInterestSchema(BaseModel):
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

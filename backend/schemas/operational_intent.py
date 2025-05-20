from typing import Any
from pydantic import BaseModel
from datetime import datetime

class TimePoint(BaseModel):
    value: datetime
    format: str

class AreaOfInterestSchema(BaseModel):
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

    class Settings:
        name = "operational_intent"


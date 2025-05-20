from typing import Any
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class TimePoint(BaseModel):
    value: datetime
    format: str

class CreateOperationalIntentRequest(BaseModel):
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

    class Settings:
        name = "operational_intent"


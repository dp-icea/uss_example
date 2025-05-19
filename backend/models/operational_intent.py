from beanie import Document
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Any

class TimePoint(BaseModel):
    value: datetime
    format: str

class OperationalIntent(Document):
    entity_id: UUID
    volume: Any
    time_start: TimePoint
    time_end: TimePoint

    class Settings:
        name = "operational_intent"

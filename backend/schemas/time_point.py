from pydantic import BaseModel
from datetime import datetime

class TimePoint(BaseModel):
    value: datetime
    format: str

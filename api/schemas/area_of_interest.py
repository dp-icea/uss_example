from pydantic import BaseModel
from typing import Any

from schema_types.datetime import DatetimeSchema

class AreaOfInterestSchema(BaseModel):
    volume: Any
    time_start: DatetimeSchema
    time_end: DatetimeSchema

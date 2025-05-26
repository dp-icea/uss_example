from pydantic import BaseModel
from datetime import datetime, timezone

class TimePoint(BaseModel):
    value: datetime
    format: str

    class Config:
        json_encoders = {
            # TODO: I guess this should somehow consider the timezone, but I still dont understand how to send timezone times to the DSS service
            datetime: lambda v: v.isoformat('T').replace("+00:00", "") + 'Z'
        }


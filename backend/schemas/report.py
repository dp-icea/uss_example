from uuid import UUID
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, HttpUrl

from schema_types.datetime import DatetimeSchema
from schemas.area_of_interest import AreaOfInterestSchema
from schema_types.subscription import SubscriptionBaseSchema
from schema_types.constraint import ConstraintUSSAvailability, ConstraintState

class ExchangeSchema(BaseModel):
    url: HttpUrl
    method: str
    headers: List[Any]
    recorder_role: str
    request_time: DatetimeSchema
    request_body: str
    response_time: DatetimeSchema
    response_body: str
    response_code: int
    problem: str

class ReportRequest(BaseModel):
    report_id: Optional[str]
    exchange: ExchangeSchema

class ReportResponse(BaseModel):
    report_id: str
    exchange: ExchangeSchema


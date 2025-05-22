from beanie import Document
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from schemas.operational_intent import TimePoint, AreaOfInterestSchema, OperationalIntentDetails
from schemas.operational_intent_reference import OperationalIntentReference
from typing import Any, List


class OperationalIntentModel(Document):
    reference: OperationalIntentReference
    details: OperationalIntentDetails

    class Settings:
        name = "operational_intent"

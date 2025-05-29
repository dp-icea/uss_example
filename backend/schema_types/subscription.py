from uuid import UUID
from typing import List
from pydantic import BaseModel, HttpUrl

class NewSubscriptionSchema(BaseModel):
    uss_base_url: HttpUrl
    notify_for_constraints: bool

class SubscriptionBaseSchema(BaseModel):
    subscription_id: UUID
    notification_index: int

class SubscriberSchema(BaseModel):
    subscriptions: List[SubscriptionBaseSchema]
    uss_base_url: HttpUrl

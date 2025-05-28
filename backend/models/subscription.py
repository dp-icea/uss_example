from beanie import Document

from schemas.subscription import SubscriptionSchema

class SubscriptionModel(Document):
    subscription: SubscriptionSchema

    class Settings:
        name = "subscription"

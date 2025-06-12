from beanie import Document

from schemas.operational_intent import OperationalIntentSchema

class OperationalIntentModel(Document):
    operational_intent: OperationalIntentSchema

    class Settings:
        name = "operational_intent"

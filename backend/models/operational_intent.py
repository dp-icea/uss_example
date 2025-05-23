from beanie import Document
from schemas.operational_intent import OperationalIntentDetails
from schemas.operational_intent_reference import OperationalIntentReference


class OperationalIntentModel(Document):
    reference: OperationalIntentReference
    details: OperationalIntentDetails

    class Settings:
        name = "operational_intent"

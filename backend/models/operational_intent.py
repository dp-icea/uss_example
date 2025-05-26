from beanie import Document

from schemas.operational_intent import OperationalIntentDetailSchema, OperationalIntentReferenceSchema

class OperationalIntentModel(Document):
    reference: OperationalIntentReferenceSchema
    details: OperationalIntentDetailSchema

    class Settings:
        name = "operational_intent"

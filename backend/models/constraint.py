from beanie import Document

from schemas.constraint import ConstraintDetailSchema, ConstraintReferenceSchema

class ConstraintModel(Document):
    reference: ConstraintReferenceSchema
    details: ConstraintDetailSchema

    class Settings:
        name = "constraint"

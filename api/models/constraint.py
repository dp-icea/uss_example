from beanie import Document

from schemas.constraint import ConstraintSchema

class ConstraintModel(Document):
    constraint: ConstraintSchema

    class Settings:
        name = "constraint"

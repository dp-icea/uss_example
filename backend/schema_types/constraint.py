from enum import Enum

# TODO: All those things are copied from the schemas.operational_intent_reference.py
# should change when testing with constraints
class ConstraintState(str, Enum):
    ACCEPTED = "Accepted"
    ACTIVATED = "Activated"
    NONCONFORMING = "Nonconforming"

class ConstraintUSSAvailability(str, Enum):
    UNKNOWN = "Unknown"


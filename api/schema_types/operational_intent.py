from enum import Enum

class OperationalIntentState(str, Enum):
    ACCEPTED = "Accepted"
    ACTIVATED = "Activated"
    NONCONFORMING = "Nonconforming"
    DELETED = "Deleted"

class OperationalIntentUSSAvailability(str, Enum):
    UNKNOWN = "Unknown"

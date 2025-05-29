from enum import Enum

class USSAvailability(str, Enum):
    """
    Enum representing the availability status of a USS (UAS Service Supplier).
    """
    DOWN = "Down"
    NORMAL = "Normal"
    UNKNOWN = "Unknown"

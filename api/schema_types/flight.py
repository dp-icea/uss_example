from enum import Enum

class FlightType(str, Enum):
    """
    Enum for the flight type.
    """
    VLOS = "VLOS"
    BVLOS = "BVLOS"

from enum import Enum

class Audition(str, Enum):
    DSS = "core-service"

class Scope(str, Enum):
    CONSTRAINT_PROCESSING = "utm.constraint_processing"
    STRATEGIC_COORDINATION = "utm.strategic_coordination"
    CONSTRAINT_MANAGEMENT = "utm.constraint_management"
    CONFORMANCE_MONITORING_SA = "utm.conformance_monitoring_sa"
    AVAILABILITY_ARBITRATION = "utm.availability_arbitration"


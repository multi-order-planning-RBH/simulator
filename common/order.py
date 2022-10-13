from enum import Enum
class OrderEnum(Enum):
    CREATED = "CREATED"
    COOKING = "COOKING"
    ASSIGNED = "ASSIGNED"
    READY = "READY"
    PICKED_UP = "PICKED_UP"
    DELIVERING  = "DELIVERING"
    DELIVERED = "DELIVERED"
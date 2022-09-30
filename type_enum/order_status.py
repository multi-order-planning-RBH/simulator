from enum import Enum
class OrderStatusEnum(Enum):
    CREATED = 1 
    ASSIGNED = 2
    COOKING = 3
    COOKED = 4
    DELIVERING = 5
    DELIVERED = 6

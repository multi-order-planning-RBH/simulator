from typing import List
from random import uniform

LocationType = List[float, float]

from enum import Enum
class LocationEnum(Enum):
    RESTAURANT = 1
    CUSTOMER = 2

def generateBangkokLocation() -> LocationType:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return [x,y]
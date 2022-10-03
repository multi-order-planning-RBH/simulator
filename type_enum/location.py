from typing import List
from random import uniform

LocationType = List[float]

from enum import Enum
class LocationEnum(Enum):
    RESTAURANT = "RESTAURANT"
    CUSTOMER = "CUSTOMER"

class Coordinates():

    def __init__(self, x : float = 0, y : float = 0):
        self.x = x
        self.y = y

    def __init__(self, other):
        self.x = other.x
        self.y = other.y

    def __radd__(self, other):
        self.x += other.x
        self.y += other.y

    def __rsub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __rdiv__(self, other):
        self.x /= other
        self.y /= other


def generateBangkokLocation_2() -> Coordinates:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return Coordinates(x, y)

def generateBangkokLocation() -> LocationType:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return [x,y]
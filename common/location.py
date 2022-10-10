from typing import List
from random import uniform

LocationType = List[float]

from enum import Enum
class LocationEnum(Enum):
    RESTAURANT = "RESTAURANT"
    CUSTOMER = "CUSTOMER"

class Coordinates():

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self.x = args[0]
            self.y = args[1]

        elif len(args) == 1:
            location = args[0]
            self.x = location.x
            self.y = location.y
        elif len(args) == 0:
            self.x = 0
            self.y = 0

    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __truediv__(self, other):
        self.x /= other
        self.y /= other
        return self


def generateBangkokLocation_2() -> Coordinates:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return Coordinates(x, y)

def generateBangkokLocation() -> LocationType:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return [x,y]

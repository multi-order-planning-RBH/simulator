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
        temp = Coordinates(self)
        temp.x += other.x
        temp.y += other.y
        return temp

    def __sub__(self, other):
        temp = Coordinates(self)
        temp.x -= other.x
        temp.y -= other.y
        return temp

    def __truediv__(self, other):
        temp = Coordinates(self)
        temp.x /= other
        temp.y /= other
        return temp

    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"

    def __float__(self):
        return (self.x**2+self.y**2)**(1/2)


def generateBangkokLocation_2() -> Coordinates:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return Coordinates(x, y)

def generateBangkokLocation() -> LocationType:
    x = uniform(13.496034, 13.949613)
    y = uniform(100.410055, 100.912941)
    return [x,y]

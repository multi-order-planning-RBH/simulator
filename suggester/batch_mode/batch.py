from typing import List
from rider.rider import Destination
from order_restaurant.order_restaurant_simulator import Order

class Batch :
    def __init__(self, destinations : List[Destination] = [], orders : List[Order] = []):
        self.orders : List[Order] = orders
        self.destinations : List[Destination] = destinations
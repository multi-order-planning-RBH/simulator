from order_restaurant.order_restaurant_simulator import Order
from common.location import Coordinates

class Batch:
    def __init__(self, orders: list[Order], destinations: list[Coordinates]):
        self.orders = orders
        self.destinations = destinations

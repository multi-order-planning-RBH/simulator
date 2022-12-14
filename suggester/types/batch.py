from order_restaurant.order_restaurant_simulator import Order
from rider.rider import Destination


class Batch:
    def __init__(self, orders: list[Order], destinations: list[Destination]):
        self.orders = orders
        self.destinations = destinations

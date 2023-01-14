import sys
import os

sys.path.append(os.path.abspath("./"))
from order_restaurant.order_restaurant_simulator import Order
from rider.rider import Rider
from rider.rider import Destination

class OnlineMode:
    def __init__(self):
        pass

    def suggest(self, order: Order, riders: list[Rider]):
        pass

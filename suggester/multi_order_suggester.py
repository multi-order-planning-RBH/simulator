from typing import Dict, List
import random

from order_restaurant.order_restaurant_simulator import OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch
from rider.rider import Rider
from suggester.batch_mode.batch_mode import batchmode

class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator
        self.batchmode = batchmode

    # randomly assign each order to a rider

    def assign_order_to_rider(self, time):
        rider_list = self.rider_simulator.unassigned_riders
        order_list = self.order_simulator.unassigned_order_list

        if len(rider_list) <= 0 or len(order_list) <= 0:
            return

        for order in order_list:
            rider = random.choice(rider_list)
            self.rider_simulator.assign_order_to_a_rider(order, rider, time)
            """if len(rider_list) > 0:
                rider = random.choice(rider_list)
                self.rider_simulator.assign_order_to_a_rider(
                    order, rider, time)
                rider_list.remove(rider)"""
    
    # Suggest candidated rider with batch mode 
    def suggest_batch_mode(self, time) -> Dict[Rider, List[Batch]]:
        riders= self.rider_simulator.unassigned_riders
        orders = self.order_simulator.unassigned_order_list
        suggested_rider_batch_graph = self.batchmode.suggest(orders, riders, time)

        

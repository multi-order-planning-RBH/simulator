import random
from order.order_simulator import OrderSimulator
from rider.riderSimulator import RiderSimulator

class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator

    # randomly assign each order to a rider
    def assign_order_to_rider(self):
        rider_list = self.rider_simulator.unassigned_riders
        order_list = self.order_simulator.unassigned_order_list

        for order in order_list:
            rider = random.choice(rider_list)
            self.rider_simulator.assign_order_to_a_rider(order, rider)
        
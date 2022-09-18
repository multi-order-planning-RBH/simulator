import random

class MultiOrderSuggester:
    def __init__(self):
        self.rider_simulator = None
        self.order_simulator = None

    # randomly assign each order to a rider
    def assign_order_to_rider(self):
        rider_list = self.rider_simulator.rider_list #list of available Riders
        order_list = self.order_simulator.order_list #list of Orders

        for order in order_list:
            rider = random.choice(rider_list)
            self.rider_simulator.assign_order_to_a_rider(order, rider)
        
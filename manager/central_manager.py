from ast import Or
import sys, os
sys.path.append(os.path.abspath("./"))

from order.order_simulator import OrderSimulator
from rider.riderSimulator import RiderSimulator
from restaurant.restaurant_simulator import RestaurantSimulator
from suggester.multi_order_suggester import MultiOrderSuggester


class CentralManager:
    def __init__(self, rider_simulator: RiderSimulator, restaurant_simulator: RestaurantSimulator, 
        order_simulator: OrderSimulator, multi_order_suggester: MultiOrderSuggester):

        self.current_time = 0
        self.rider_simulator = rider_simulator
        self.restaurant_simulator = restaurant_simulator
        self.order_simulator = order_simulator
        self.multi_order_suggester = multi_order_suggester
        
    def calculate_customer_waiting_time(self):
        sum_waiting_time = 0
        for order in self.order_simulator.finished_order_list:
            sum_waiting_time = order.finished_time - order.created_time
        
        return sum_waiting_time / len(self.order_simulator.finished_order_list)
            

    def calculate_rider_availability(self):
        pass

    def simulate(self, total_time: int, time_window: int):
        while self.current_time < total_time:
            self.order_simulator.simulate()
            self.restaurant_simulator.simulate()
            self.rider_simulator.simulate()

            if self.current_time > 0 and self.current_time % time_window == 0:
                self.multi_order_suggester.assign_order_to_rider()

            self.current_time += 1

def main():
    order = OrderSimulator()
    restaurant = RestaurantSimulator()
    rider = RiderSimulator()
    multi_order = MultiOrderSuggester(rider_simulator=rider, order_simulator=order)

    manager = CentralManager(rider_simulator=rider, restaurant_simulator=restaurant, order_simulator=order)
    print("manager")

if __name__ == "__main__":
    main()

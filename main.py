from manager.central_manager import CentralManager
from rider.rider_simulator import rider_simulator
from order_restaurant.order_restaurant_simulator import order_simulator, restaurant_simulator
from suggester.multi_order_suggester import MultiOrderSuggester
import time

def main():
    start = time.time()
    order = order_simulator
    restaurant = restaurant_simulator
    rider = rider_simulator
    multi_order = MultiOrderSuggester(rider_simulator=rider, order_simulator=order)

    manager = CentralManager(rider_simulator=rider, restaurant_simulator=restaurant, order_simulator=order, multi_order_suggester=multi_order)
    manager.simulate(10001, 10)

    print("Customer Waiting Time:           ", manager.calculate_customer_waiting_time())
    print("Rider onroad time:               ", manager.calculate_rider_utilization_time())
    print("Number of order:                 ", manager.calculate_rider_order_count())
    print("Computation time:                ", time.time()-start)
    print("Number of assigning:             ", rider_simulator.count)
    print("Number of success assigning:     ", rider_simulator.success_count)
if __name__ == "__main__":
    main()

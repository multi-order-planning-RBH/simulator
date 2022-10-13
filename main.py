from manager.central_manager import CentralManager
from rider.riderSimulator import RiderSimulator
from order.order_simulator import OrderSimulator

from restaurant.restaurant_simulator import RestaurantSimulator
from suggester.multi_order_suggester import MultiOrderSuggester

def main():
    order = OrderSimulator()
    restaurant = RestaurantSimulator()
    rider = RiderSimulator()
    multi_order = MultiOrderSuggester(rider_simulator=rider, order_simulator=order)

    manager = CentralManager(rider_simulator=rider, restaurant_simulator=restaurant, order_simulator=order, multi_order_suggester=multi_order)
    manager.simulate(100, 10)

    print("Customer Waiting Time:", manager.calculate_customer_waiting_time())
    print("Rider Availability:", manager.calculate_rider_availability())

if __name__ == "__main__":
    main()
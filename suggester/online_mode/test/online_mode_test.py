import sys, os
sys.path.append(os.path.abspath("./"))

from suggester.online_mode.online_mode import online_mode
from order_restaurant.order_restaurant_simulator import order_simulator, restaurant_simulator
from rider.rider_simulator import rider_simulator
from rider.rider import Rider

for time in range(10):
    order_simulator.simulate(time)
    restaurant_simulator.simulate(time)
    rider_simulator.simulate(time)

    rider, _ = online_mode.find_best_insertion(order_simulator.unassigned_order_list[0], rider_simulator.riders, time)
    rider_simulator.assign_order_to_a_rider(order_simulator.unassigned_order_list[0], rider, time)

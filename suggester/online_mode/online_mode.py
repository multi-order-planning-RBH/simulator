import sys
import os
import numpy as np

sys.path.append(os.path.abspath("./"))
from order_restaurant.order_restaurant_simulator import Order
from rider.rider import Rider
from rider.rider import Destination
from common.location import LocationEnum
from ml_estimator.traveling_time import estimate_traveling_time

class OnlineMode:
    def __init__(self):
        # TODO: add max order
        pass

    def suggest(self, order: Order, riders: list[Rider], time: int):
        rider, destinations = self.find_best_insertion(order, riders, time)
        # TODO: assign new destinations list to the rider

    def find_best_insertion(self, order: Order, riders: list[Rider], time: int):
        min_cost = np.inf
        for rider in riders:
            cost, destinations = self.plain_insertion(order, rider, time)
            if cost < min_cost:
                best_rider = rider
                best_destinations = destinations
                
        return best_rider, best_destinations

    def plain_insertion(self, order: Order, rider: Rider, time: int):
        if rider.current_destination is None:
            # rider has no order
            new_destinations = list(rider.destinations)
            new_destinations.append(order.restaurant_destination)
            new_destinations.append(order.customer_destination)
            cost = self.calculate_cost(new_destinations, order.restaurant_destination, time)
            return cost, new_destinations

        current_idx = rider.destinations.index(rider.current_destination)
        min_cost = np.inf
        for i in range(current_idx, len(rider.destinations) + 1, 1):
            for j in range(i + 1, len(rider.destinations) + 2, 1):
                new_destinations = list(rider.destinations)
                new_destinations.insert(i, order.restaurant_destination)
                new_destinations.insert(j, order.customer_destination)

                cost = self.calculate_cost(new_destinations, rider.current_destination, time)
                if min_cost > cost:
                    best_destinations = new_destinations

        return min_cost, best_destinations
        
    def calculate_cost(self, old_destinations: list[Destination], new_destinations: list[Destination], current_destination: Destination, time: int):
        return self.calculate_finished_time(new_destinations, current_destination, time) - self.calculate_finished_time(old_destinations, current_destination, time)

    def calculate_finished_time(self, destinations: list[Destination], current_destination: Destination, time: int):
        current_time = time
        current_idx = destinations.index(current_destination)
        for idx in range(current_idx + 1, len(destinations)):
            current_time += estimate_traveling_time(destinations[idx - 1].location, destinations[idx].location)
            if destinations[idx].type == LocationEnum.RESTAURANT:
                if destinations[idx].order.assigned_time is None:
                    # new order has not been assigned. so we use time + estimated preparing time
                    current_time = max(current_time, time + destinations[idx].preparing_duration)
                else:
                    # assigned order
                    current_time = max(current_time, destinations[idx].order.assigned_time + destinations[idx].preparing_duration)
                
        return current_time

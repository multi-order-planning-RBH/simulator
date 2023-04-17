from ml_estimator.traveling_time import estimate_traveling_time
from common.location import LocationEnum
from rider.rider import Destination
from rider.rider import Rider
from order_restaurant.order_restaurant_simulator import Order
import sys
import os
import numpy as np
from config import Config

sys.path.append(os.path.abspath("./"))


class OnlineMode:
    def __init__(self, max_order=3):
        self.max_order = max_order

    def find_best_insertion(self, order: Order, riders: list[Rider], time: int):
        best_rider = None
        best_destinations = None
        min_cost = np.inf

        for rider in riders:
            num_orders = 0
            if rider.current_destination is not None and rider.current_destination.type == LocationEnum.CUSTOMER:
                num_orders += 1
            for destination in rider.destinations:
                if destination.type == LocationEnum.CUSTOMER:
                    num_orders += 1

            if num_orders >= self.max_order:
                continue

            cost, destinations = self.plain_insertion(order, rider, time)
            if cost < min_cost:
                min_cost = cost
                best_rider = rider
                best_destinations = destinations

        return best_rider, best_destinations

    def plain_insertion(self, order: Order, rider: Rider, time: int):
        if rider.current_destination is None or rider.order_count == 0:
            # rider has no order
            new_destinations = list(rider.destinations)
            new_destinations.append(order.restaurant_destination)
            new_destinations.append(order.customer_destination)

            new_finished_time = self.calculate_finished_time(
                new_destinations, rider, time)
            cost = new_finished_time - time
            return cost, new_destinations

        # old_finished_time = self.calculate_finished_time(
        #    rider.destinations, rider, time)

        # init min_cost and best_destinations
        best_destinations = rider.destinations + \
            [order.restaurant_destination, order.customer_destination]
        new_finished_time = self.calculate_finished_time(
            best_destinations, rider, time)
        min_cost = new_finished_time - time

        for i in range(len(rider.destinations)):
            for j in range(i + 1, len(rider.destinations) + 2):
                new_destinations = list(rider.destinations)
                new_destinations.insert(i, order.restaurant_destination)
                new_destinations.insert(j, order.customer_destination)

                new_finished_time = self.calculate_finished_time(
                    new_destinations, rider, time)
                cost = new_finished_time - time
                if min_cost > cost:
                    min_cost = cost
                    best_destinations = new_destinations

        return min_cost, best_destinations

    def calculate_finished_time(self, destinations: list[Destination], rider: Rider, time: int):
        current_time = time
        current_location = rider.location

        if rider.current_destination is not None:
            current_time += estimate_traveling_time(
                current_location, rider.current_destination.location)
            current_location = rider.current_destination.location

        for destination in destinations:
            current_time += estimate_traveling_time(
                current_location, destination.location)
            current_location = destination.location

            if destination.type == LocationEnum.RESTAURANT:
                if destination.order.assigned_time is None:
                    # new order has not been assigned. so we use time + estimated preparing time
                    current_time = max(current_time, time +
                                       destination.preparing_duration)
                else:
                    # assigned order
                    current_time = max(
                        current_time, destination.order.assigned_time + destination.preparing_duration)

        return current_time


onlinemode = OnlineMode(Config.MAX_ORDER_PER_RIDER)

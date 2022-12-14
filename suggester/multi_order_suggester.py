import random
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch
from rider.rider import Destination
from common.location import Coordinates, LocationEnum
from itertools import permutations


class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator

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

    def construct_order_graph(self, orders: list[Order]) -> dict[Batch, dict[Batch, int]]:
        batches = list()
        for order in orders:
            batch = Batch(
                [order], [order.restaurant_location, order.destination])
            batches.append(batch)

        order_graph = dict()
        for batch in batches:
            edges = dict()
            for neighbor in batches:
                if neighbor == batch:
                    continue

                edges[neighbor] = self.calculate_order_graph_weight(
                    batch, neighbor)

            order_graph[batch] = edges

        return order_graph

    # ML
    def estimate_traveling_time(self, start: Coordinates, stop: Coordinates) -> int:
        return 0

    # time it takes for an order to finish using a journey(destinations)
    def calculate_expected_delivery_time(self, order: Order, destinations: list[Destination]) -> int:
        for idx in range(len(destinations)):
            if idx == 0:
                current_time = destinations[idx].ready_time
                continue

            current_time += self.estimate_traveling_time(
                destinations[idx - 1].location, destinations[idx].location)

            if destinations[idx].type == LocationEnum.RESTAURANT:
                current_time = max(current_time, destinations[idx].ready_time)

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # shortest time possible
    def calculate_shortest_delivery_time(self, order: Order) -> int:
        return (order.meal_finished_time - order.created_time) + self.estimate_traveling_time(order.restaurant_location, order.destination)

    # expected - shortest
    def calculate_extra_delivery_time(self, order: Order, destinations: list[Destination]) -> int:
        return self.calculate_expected_delivery_time(order, destinations) - self.calculate_shortest_delivery_time(order)

    # cost of a journey
    def calculate_cost(self, orders: list[Order], destinations: list[Destination]) -> int:
        cost = 0
        for order in orders:
            cost += self.calculate_extra_delivery_time(order, destinations)
        return cost

    # check if restaurant destination are always before customer destination
    def is_valid_journey(self, destinations: list[Destination]) -> bool:
        orders = set()
        for destination in destinations:
            if destination.type == LocationEnum.RESTAURANT:
                orders.add(destination.order)
            elif destination.type == LocationEnum.CUSTOMER and destination.order not in orders:
                return False
        return True

    # brute-force
    def calculate_order_graph_weight(self, batch: Batch, neighbor: Batch) -> tuple[int, list[Destination]]:
        orders = batch.orders + neighbor.orders
        all_destinations = batch.destinations + neighbor.destinations

        best_destinations = list(all_destinations)
        min_cost = self.calculate_cost(orders, all_destinations)
        for permutation in list(permutations(all_destinations)):
            destinations = list(permutation)
            if not self.is_valid_journey(destinations):
                continue
            cost = self.calculate_cost(orders, destinations)
            if cost < min_cost:
                best_destinations = list(destinations)
                min_cost = cost

        return min_cost, best_destinations

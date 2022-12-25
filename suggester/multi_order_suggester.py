import random
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch
from rider.rider import Destination
from common.location import Coordinates, LocationEnum
from itertools import permutations
from rider.rider import Rider
from ml_estimator.traveling_time import estimate_traveling_time
import heapq


class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator
        # this should be params
        self.max_order_per_batch = 2

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

    # merge orders into batch
    def batch_order(self, orders_graph: dict[Batch, dict[Batch, int]], edge_heap: list[int, Batch, Batch]) -> list[Batch]:

        max_order = self.max_order_per_batch
        merged_order = set()
        all_cost = sum([self.calculate_cost_order_graph(
            batch.orders, batch.destinations) for batch in orders_graph])
        num_batch = len(orders_graph)

        # default value from paper, should tune this value too
        threhold_cost = 60
        while all_cost/num_batch <= threhold_cost and len(edge_heap) > 0:

            min_edge_weight, min_batch, min_neighbor = heapq.heappop(edge_heap)
            if len(min_batch.orders) + len(min_neighbor.orders) > max_order:
                continue
            if min_batch in merged_order or min_neighbor in merged_order:
                continue

            # remove batches to merge

            merged_order.add(min_batch)
            merged_order.add(min_neighbor)
            orders_graph.pop(min_batch, None)
            orders_graph.pop(min_neighbor, None)

            # create new batch
            new_orders = min_batch.orders+min_neighbor.orders
            _, new_destinations = self.calculate_order_graph_weight(
                min_batch, min_neighbor)
            new_batch = Batch(orders=new_orders, destinations=new_destinations)
            new_edge_weight = {neighbor: self.calculate_order_graph_weight(new_batch, neighbor)[
                0] for neighbor in orders_graph if len(neighbor.orders)+len(new_batch.orders) <= max_order}

            # remove edge to unmerged batch + add new edge to merged batch
            for batch in orders_graph:
                orders_graph[batch].pop(min_batch, None)
                orders_graph[batch].pop(min_neighbor, None)

                if batch not in new_edge_weight:
                    continue

                orders_graph[batch][new_batch] = new_edge_weight[batch]
                heapq.heappush(
                    edge_heap, [new_edge_weight[batch], batch, new_batch])

            orders_graph[new_batch] = new_edge_weight
            all_cost += min_edge_weight
            num_batch -= 1
        return [batch for batch in orders_graph]

    def construct_order_graph(self, orders: list[Order]) -> dict[Batch, dict[Batch, int]]:

        edge_list = []

        batches = list()
        for order in orders:
            batch = Batch(
                [order], [order.restaurant_destination, order.customer_destination])
            batches.append(batch)

        order_graph = dict()
        for batch in batches:
            edges = dict()
            for neighbor in batches:
                if neighbor == batch:
                    continue

                edges[neighbor], _ = self.calculate_order_graph_weight(
                    batch, neighbor)
            order_graph[batch] = edges

        for i in range(len(batches)):
            for j in range(i+1, len(batches)):
                batch = batches[i]
                neighbor = batches[j]
                edge_list.append(
                    [order_graph[batch][neighbor], batch, neighbor])

        heapq.heapify(edge_list)
        return order_graph, edge_list

    # time it takes to finish an order using a journey(destinations)
    # using destinations[0] as initial localtion
    def calculate_expected_delivery_time_order_graph(self, order: Order, destinations: list[Destination]) -> int:
        for idx in range(len(destinations)):
            if idx == 0:
                current_time = destinations[idx].preparing_duration
                continue

            current_time += estimate_traveling_time(
                destinations[idx - 1].location, destinations[idx].location)

            if destinations[idx].type == LocationEnum.RESTAURANT:
                current_time = max(
                    current_time, destinations[idx].preparing_duration)

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # shortest time possible
    def calculate_shortest_delivery_time(self, order: Order) -> int:
        return order.estimated_cooking_duration + estimate_traveling_time(order.restaurant_destination, order.customer_destination)

    # expected - shortest
    def calculate_extra_delivery_time_order_graph(self, order: Order, destinations: list[Destination]) -> int:
        return self.calculate_expected_delivery_time_order_graph(order, destinations) - self.calculate_shortest_delivery_time(order)

    # cost of a journey
    def calculate_cost_order_graph(self, orders: list[Order], destinations: list[Destination]) -> int:
        cost = 0
        for order in orders:
            cost += self.calculate_extra_delivery_time_order_graph(
                order, destinations)
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

    # [brute-force] finding best journey and calculate weight
    def calculate_order_graph_weight(self, batch: Batch, neighbor: Batch) -> tuple[int, list[Destination]]:
        orders = batch.orders + neighbor.orders
        all_destinations = batch.destinations + neighbor.destinations

        best_destinations = list(all_destinations)
        min_cost = self.calculate_cost_order_graph(orders, all_destinations)
        for permutation in list(permutations(all_destinations)):
            destinations = list(permutation)
            if not self.is_valid_journey(destinations):
                continue
            cost = self.calculate_cost_order_graph(orders, destinations)
            if cost < min_cost:
                best_destinations = list(destinations)
                min_cost = cost

        weight = min_cost\
            - self.calculate_cost_order_graph(batch.orders, batch.destinations)\
            - self.calculate_cost_order_graph(
                neighbor.orders, neighbor.destinations)

        return weight, best_destinations

    def construct_food_graph(self, batches: list[Batch], riders: list[Rider], current_time: int) -> dict[Rider, dict[Batch, int]]:
        food_graph = dict()
        for rider in riders:
            edges = dict()
            for batch in batches:
                edges[batch] = self.calculate_food_graph_weight(
                    batch, rider, current_time)
            food_graph[rider] = edges
        return food_graph

    # sum of extra delivery time
    def calculate_food_graph_weight(self, batch: Batch, rider: Rider, current_time: int) -> int:
        cost = 0
        for order in batch.orders:
            cost += self.calculate_extra_delivery_time_food_graph(
                order, batch.destinations, rider, current_time)
        return cost

    # time it takes to finish an order using a journey(destinations)
    # using rider as initial localtion
    def calculate_expected_delivery_time_food_graph(self, order: Order, destinations: list[Destination], rider: Rider, current_time: int) -> int:
        ready_times = []
        for idx in range(len(destinations)):
            ready_times.append(
                current_time + destinations[idx].preparing_duration)

        for idx in range(len(destinations)):
            if idx == 0:
                current_time += estimate_traveling_time(
                    rider.location, destinations[idx].location)

                current_time = max(
                    current_time, ready_times[idx])
                continue

            current_time += estimate_traveling_time(
                destinations[idx - 1].location, destinations[idx].location)

            if destinations[idx].type == LocationEnum.RESTAURANT:
                current_time = max(
                    current_time, ready_times[idx])

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # expected - shortest
    def calculate_extra_delivery_time_food_graph(self, order: Order, destinations: list[Destination], rider: Rider, current_time: int) -> int:
        return self.calculate_expected_delivery_time_food_graph(order, destinations, rider, current_time) - self.calculate_shortest_delivery_time(order)

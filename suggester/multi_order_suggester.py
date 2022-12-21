import random
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch
from rider.rider import Destination
from common.location import Coordinates, LocationEnum
from itertools import permutations
from rider.rider import Rider
import scipy

class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator
        # this should be params 
        self.max_order_per_batch = 3
        self.order_estimated_finish_time = {}

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
    def batch_order(self,orders_graph: dict[Batch, dict[Batch, int]]) -> list[Batch]:

        
        max_order = self.max_order_per_batch

        all_cost = sum([self.calculate_cost_order_graph(batch.orders,batch.destinations) for batch in orders_graph])
        num_batch = len(orders_graph)

        # default value from paper, should tune this value too
        threhold_cost = 60
        while all_cost/num_batch <= threhold_cost:

            # find min weight in the graph
            # heap should be used  
            min_batch = min_neighbor = None
            min_edge_weight = float('inf')
            for batch in orders_graph:
                for neighbor in orders_graph[batch]:
                    if orders_graph[batch][neighbor] < min_edge_weight \
                        and len(batch.orders) + len(neighbor.orders)<=max_order:

                        min_batch = batch
                        min_neighbor = neighbor
                        min_edge_weight = orders_graph[batch][neighbor]
            
            # if cannot find edge that meet requirement 
            if not min_batch:
                break
            
            # remove batches to merge
            orders_graph.pop(min_batch,None)
            orders_graph.pop(min_neighbor,None)

            # create new batch 
            new_orders =min_batch.orders+min_neighbor.orders
            _,new_destinations = self.calculate_order_graph_weight(min_batch,min_neighbor)

            new_batch = Batch(orders=new_orders,destinations=new_destinations)

  
            new_edge_weight = {neighbor:self.calculate_order_graph_weight(new_batch,neighbor)[0] for neighbor in orders_graph}
            
            # remove edge to unmerged batch + add new edge to merged batch
            for batch in orders_graph:
                orders_graph[batch].pop(min_batch,None)
                orders_graph[batch].pop(min_neighbor,None)

                orders_graph[batch][new_batch] = new_edge_weight[batch]

            orders_graph[new_batch] = new_edge_weight
            all_cost+=min_edge_weight
            num_batch-=1
        return [batch for batch in orders_graph]



    def construct_order_graph(self, orders: list[Order]) -> dict[Batch, dict[Batch, int]]:

        self.order_estimated_finish_time= {}
        for order in orders:
            self.order_estimated_finish_time[order]=self.estimate_meal_finished_time(order)

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

        return order_graph

    # ML
    def estimate_traveling_time(self, start: Coordinates, stop: Coordinates) -> int:
        return 600
    
    # ML
    def estimate_meal_finished_time(self, order: Order) -> int:

        # tmp wait for ML
        mean =1000
        std=300

        lower_bound = 200
        upper_bound = 2500

        cooking_duration = int(scipy.stats.truncnorm.rvs((lower_bound-mean)/std,
                                            (upper_bound-mean)/std,
                                            loc=mean,scale=std,size=1)[0])
        if cooking_duration<=0:
            cooking_duration = 1000
        return cooking_duration

    # time it takes to finish an order using a journey(destinations)
    # using destinations[0] as initial localtion
    def calculate_expected_delivery_time_order_graph(self, order: Order, destinations: list[Destination]) -> int:
        for idx in range(len(destinations)):
            if idx == 0:
                # current_time = destinations[idx].ready_time
                current_time = self.order_estimated_finish_time[order]
                continue

            current_time += self.estimate_traveling_time(
                destinations[idx - 1].location, destinations[idx].location)

            if destinations[idx].type == LocationEnum.RESTAURANT:
                # current_time = max(current_time, destinations[idx].ready_time)
                current_time = max(current_time, self.order_estimated_finish_time[order])

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # shortest time possible
    def calculate_shortest_delivery_time(self, order: Order) -> int:
        return (self.order_estimated_finish_time[order]- order.created_time) + self.estimate_traveling_time(order.restaurant_destination, order.customer_destination)

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
        for idx in range(len(destinations)):
            if idx == 0:
                current_time += self.estimate_traveling_time(
                    rider.location, destinations[idx].location)

                current_time = max(current_time, destinations[idx].ready_time)
                continue

            current_time += self.estimate_traveling_time(
                destinations[idx - 1].location, destinations[idx].location)

            if destinations[idx].type == LocationEnum.RESTAURANT:
                current_time = max(current_time, destinations[idx].ready_time)

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # expected - shortest
    def calculate_extra_delivery_time_food_graph(self, order: Order, destinations: list[Destination], rider: Rider, current_time: int) -> int:
        return self.calculate_expected_delivery_time_food_graph(order, destinations, rider, current_time) - self.calculate_shortest_delivery_time(order)

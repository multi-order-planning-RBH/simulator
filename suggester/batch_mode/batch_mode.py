from scipy.optimize import milp, LinearConstraint, Bounds
from collections import defaultdict
import numpy as np
from math import ceil
from typing import Dict, List, Tuple, Set
import sys, os
import heapq

sys.path.append(os.path.abspath("./"))
from order_restaurant.order_restaurant_simulator import Order
from suggester.types.batch import Batch
from rider.rider import Destination
from common.location import LocationEnum
from itertools import permutations
from rider.rider import Rider
from ml_estimator.traveling_time import estimate_traveling_time


class BatchMode:

    def __init__(self):
        # this should be params
        self.max_order_per_batch = 2

    # Suggest candidated rider by 
    def suggest(self, orders: list[Order], riders: list[Rider], time, for_test: bool = False) -> Dict[Rider, List[Batch]]:
        
        riders = [[rider.id,rider] for rider in riders]
        orders = [[order.id,order] for order in orders]

        riders = [rider for _,rider in riders]
        orders = [order for _,order in orders]


        #Construct order graph
        order_graph, edge_list = self.construct_order_graph(orders)
        #Batch and create order graph
        batches = self.batch_order(order_graph ,edge_list)
        #Construct food graph
        food_graph = self.construct_food_graph(batches, riders, time)
        #Suggest rider
        suggested_rider_batch_graph = self.rider_suggester(food_graph)

        if for_test:
            return order_graph, edge_list, batches, food_graph, suggested_rider_batch_graph
        
        return suggested_rider_batch_graph   

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
            for j in range(i+1,len(batches)):
                batch=batches[i]
                neighbor=batches[j]
                edge_list.append([order_graph[batch][neighbor],batch,neighbor])
        
        heapq.heapify(edge_list)
        return order_graph ,edge_list

    # merge orders into batch
    def batch_order(self,orders_graph: dict[Batch, dict[Batch, int]], edge_heap: list[int,Batch,Batch]) -> list[Batch]:

        max_order = self.max_order_per_batch
        merged_order = set()
        all_cost = sum([self.calculate_cost_order_graph(batch.orders,batch.destinations) for batch in orders_graph])
        num_batch = len(orders_graph)

        # default value from paper, should tune this value too

        # this should be params
        threhold_cost = 600

        while all_cost/num_batch <= threhold_cost and len(edge_heap)>0:
            
            min_edge_weight,min_batch,min_neighbor = heapq.heappop(edge_heap)
            if len(min_batch.orders) + len(min_neighbor.orders) > max_order:
                continue
            if min_batch in merged_order or min_neighbor in merged_order:
                continue
            
            # remove batches to merge

            merged_order.add(min_batch)
            merged_order.add(min_neighbor)
            orders_graph.pop(min_batch,None)
            orders_graph.pop(min_neighbor,None)

            # create new batch 
            new_orders =min_batch.orders+min_neighbor.orders
            _,new_destinations = self.calculate_order_graph_weight(min_batch,min_neighbor)
            new_batch = Batch(orders=new_orders,destinations=new_destinations)
            new_edge_weight = {neighbor:self.calculate_order_graph_weight(new_batch,neighbor)[0] for neighbor in orders_graph if len(neighbor.orders)+len(new_batch.orders)<=max_order}
            
            # remove edge to unmerged batch + add new edge to merged batch 
            for batch in orders_graph:
                orders_graph[batch].pop(min_batch,None)
                orders_graph[batch].pop(min_neighbor,None)

                if batch not in new_edge_weight:
                    continue

                orders_graph[batch][new_batch] = new_edge_weight[batch]
                heapq.heappush(edge_heap,[new_edge_weight[batch],batch,new_batch])

            orders_graph[new_batch] = new_edge_weight
            all_cost+=min_edge_weight
            num_batch-=1
        return [batch for batch in orders_graph]

    def construct_food_graph(self, batches: list[Batch], riders: list[Rider], current_time: int) -> dict[Rider, dict[Batch, int]]:
        food_graph = dict()
        for rider in riders:
            edges = dict()
            for batch in batches:
                edges[batch] = self.calculate_food_graph_weight(
                    batch, rider, current_time)
            food_graph[rider] = edges
        return food_graph

    #Suggest rider-batch pairs based on food graph
    def rider_suggester(self, food_graph: Dict[Rider, Dict[Batch, int]]) -> Dict[Rider, List[Batch]]:
        batch_rider_order_time_array = self.get_batch_to_rider(food_graph)
        res, rider_unique = self.solve_integer_programming(batch_rider_order_time_array)
        suggested_rider_batch_graph = self.transform_res_to_graph(res, batch_rider_order_time_array, rider_unique)
        return suggested_rider_batch_graph


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
                current_time = max(current_time, destinations[idx].preparing_duration)

            if destinations[idx].order == order and destinations[idx].type == LocationEnum.CUSTOMER:
                return current_time - order.created_time

    # shortest time possible
    def calculate_shortest_delivery_time(self, order: Order) -> int:
        return order.estimated_cooking_duration+ estimate_traveling_time(order.restaurant_destination.location, order.customer_destination.location)

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
    
    #Transform food graph to table which its schema is rider batch number cost
    def get_batch_to_rider(self, food_graph: Dict[Rider, Dict[Batch, int]]) -> np.ndarray:
        batch_rider_pair_list = []
        count = 0 
        for k_r, v_r in food_graph.items():
            for k_b, v in v_r.items():
                batch_rider_pair_list.append([k_r, k_b, count, v])
                count += 1
        batch_rider_order_time_array = np.array(batch_rider_pair_list)
        return batch_rider_order_time_array

    #Construct matrices and the solve integer programming 
    def solve_integer_programming(self, batch_rider_order_time_array : np.ndarray) -> Tuple[np.ndarray, Set]: 
        rider_unique = set(batch_rider_order_time_array[:,0])
        len_rider = len(rider_unique)
        batch_unique = set(batch_rider_order_time_array[:,1])
        len_batch = len(batch_unique)
        len_A = len_rider+len_batch

        n = len(batch_rider_order_time_array)
        A = np.zeros((len_A, n))
        c = batch_rider_order_time_array[:,3]

        count = 0
        for rider in rider_unique:
            temp = batch_rider_order_time_array[:, 0] == rider 
            A[count, temp] = 1
            count += 1

        for batch in batch_unique:
            temp = batch_rider_order_time_array[:, 1] == batch 
            A[count, temp] = 1
            count += 1

        b_u = np.zeros_like(A[:, 0])
        b_l = np.zeros_like(b_u)

        u = np.full_like(A[0, :], 1)
        l = np.zeros_like(u)

        if len_rider < len_batch:
            temp = ceil(len_batch/len_rider)
            b_u[:len_rider] = temp
            b_u[len_rider:] = 2
            b_l[:len_rider] = temp
            b_l[len_rider:] = 1

        elif len_rider == len_batch:
            b_u[:] = 2
            b_l[:] = 2
        if len_rider > len_batch:
            temp = ceil(len_rider/len_batch)
            b_u[:len_rider] = 2
            b_u[len_rider:] = temp
            b_l[:len_rider] = 1
            b_l[len_rider:] = temp

        integrality = np.ones_like(batch_rider_order_time_array[:, 0])
        constraints = LinearConstraint(A, b_l, b_u)
        bounds = Bounds(lb = l, ub = u)
        res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)

        return res, rider_unique

    #Converse integer programming result to 
    def transform_res_to_graph(self, res: np.ndarray, batch_rider_order_time_array: np.ndarray, rider_unique: Set)-> Dict[Rider, List[Batch]]:
        x = res.x
        selected_x = x == 1
        selected_pair = batch_rider_order_time_array[selected_x][:, :2]

        suggested_rider_batch_graph = defaultdict(list)
        for rider in rider_unique:
            selected_batch = selected_pair[selected_pair[:, 0] == rider, :][:, 1]
            for batch in selected_batch:
                suggested_rider_batch_graph[rider].append(batch)

        return suggested_rider_batch_graph

batchmode = BatchMode()
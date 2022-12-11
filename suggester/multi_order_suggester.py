import random
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch

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
                self.rider_simulator.assign_order_to_a_rider(order, rider, time)
                rider_list.remove(rider)"""
    
    def construct_order_graph(self, orders: list[Order]) -> dict[Batch, dict[Batch, int]]:
        batches = list()
        for order in orders:
            batch = Batch([order], [order.restaurant_location, order.destination])
            batches.append(batch)

        order_graph = dict()
        for batch in batches:
            edges = dict()
            for neighbor in batches:
                if neighbor == batch:
                    continue
                
                edges[neighbor] = self.calculate_order_graph_weight(batch, neighbor)

            order_graph[batch] = edges
        
        return order_graph
    
    def calculate_order_graph_weight(self, batch: Batch, neighbor: Batch) -> int:
        return 0

        

                
        
        
from typing import Dict, List
import random

from order_restaurant.order_restaurant_simulator import OrderSimulator
from rider.rider_simulator import RiderSimulator
from suggester.types.batch import Batch
from rider.rider import Rider
from suggester.batch_mode.batch_mode import batchmode
from suggester.online_mode.online_mode import onlinemode

class MultiOrderSuggester:
    def __init__(self, rider_simulator: RiderSimulator, order_simulator: OrderSimulator):
        self.rider_simulator = rider_simulator
        self.order_simulator = order_simulator
        self.batchmode = batchmode
        self.onlinemode = onlinemode

        self.log_batch_result = []

    # randomly assign each order to a rider

    def assign_order_to_rider(self, time):
        rider_list = self.rider_simulator.unassigned_riders
        order_list = self.order_simulator.unassigned_order_list

        if len(rider_list) <= 0 or len(order_list) <= 0:
            return

        for order in order_list:
            # rider = random.choice(rider_list)
            # self.rider_simulator.assign_order_to_a_rider(order, rider, time)
            if len(rider_list) > 0:
                rider = random.choice(rider_list)
                self.rider_simulator.assign_order_to_a_rider(
                    order, rider, time)
                rider_list.remove(rider)
    
    # Suggest candidated rider with batch mode 
    def suggest_batch_mode(self, time) -> Dict[Rider, List[Batch]]:
        

        riders = sorted([[r.id,r] for r in self.rider_simulator.unassigned_riders])
        orders = sorted([[o.id,o] for o in self.order_simulator.unassigned_order_list])

        riders = [r for _,r in riders]
        orders = [o for _,o in orders]

        if len(riders)==0 or len(orders)==0:
            return
        
        suggested_rider_batch_graph = self.batchmode.suggest(orders, riders, time)

        suggested_rider_batch_graph = sorted([[-len(batch),rider.id,rider,batch] for rider,batch in suggested_rider_batch_graph.items()])

        self.log_batch_result.append([[_,rider.id] for _,__,rider,batches in suggested_rider_batch_graph])
        
        
        suggested_rider_batch_graph = [[rider,batches] for _,__,rider,batches in suggested_rider_batch_graph]

        batch2rider = {}
        for rider,batches in suggested_rider_batch_graph:
            for batch in batches:
                if batch not in batch2rider:
                    batch2rider[batch]=[]
                batch2rider[batch].append(rider)
        assigned_rider = set()
        unassigned_batch = []
        for batch in batch2rider:
            available_rider = [rider for rider in batch2rider[batch] if rider not in assigned_rider]
            if available_rider == []:
                unassigned_batch.append(batch)
                continue
            rider = random.choice(available_rider)
            assigned_rider.add(rider)
            self.rider_simulator.assign_batch_to_a_rider(batch, rider, time)
        
        unassigned_riders = [rider for rider in riders if rider not in assigned_rider]

        for idx in range(min(len(unassigned_batch),len(unassigned_riders))):
            self.rider_simulator.assign_batch_to_a_rider(unassigned_batch[idx], unassigned_riders[idx], time)
            
        

    
    def suggest_online_mode(self, time):
        riders= self.rider_simulator.working_riders
        orders = self.order_simulator.unassigned_order_list
        if len(riders)==0 or len(orders)==0:
            return

        for order in orders:
            best_rider, best_destinations = self.onlinemode.find_best_insertion(order, riders, time)
            if best_rider is None:
                continue
            self.rider_simulator.assign_online_mode_order_to_a_rider(order, best_rider, best_destinations, time)

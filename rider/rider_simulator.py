import pandas as pd

from typing import List

from rider.rider import Rider, Order
from common.order import OrderEnum
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import order_simulator, Destination
from suggester.types.batch import Batch
from config import Config
from map.map import sample_points_on_graph

class RiderSimulator():
    def __init__(self):
        self.maximum_of_rider: int 
        self.maximum_order_per_rider: int 
        self.maximum_item_per_rider: int 
        self.riders : List[Rider] = list()
        self.working_riders : List[Rider] = list()
        self.unassigned_riders : List[Rider] = list() 
        self.time = 0
        self.count = 0 
        self.success_count = 0 
        rider_initial_point = sample_points_on_graph(Config.RIDER_NUMBER)

        for i in range(Config.RIDER_NUMBER):
            self.create_rider_innitial_location(rider_initial_point[i])

    def create_rider_innitial_location(self, location, starting_time = Config.RIDER_STARTING_TIME, getoff_time = Config.RIDER_GETOFF_TIME):
        rider = Rider(id = len(self.riders), location = location, starting_time = starting_time, getoff_time = getoff_time)
        self.riders.append(rider)
        if rider.current_action == ActionEnum.NO_ACTION:
            self.working_riders.append(rider)
            self.unassigned_riders.append(rider)

        return rider

    def assign_online_mode_order_to_a_rider(self, order: Order, rider: Rider, destinations: List[Destination], time) -> bool:
        self.count += 1

        res = rider.add_online_destination(order, destinations, time)
        if res:
            self.success_count += 1
            order_simulator.change_order_status(order.id, OrderEnum.ASSIGNED, time, rider.id)
        return res

    # batch mode assignment
    def assign_batch_to_a_rider(self, batch:Batch, rider:Rider, time:int) -> bool:
        self.count += len(batch.orders)

        res = rider.add_batch_destination(batch, time)
        if res == True :
            self.success_count += 1
            for order in batch.orders:
                order_simulator.change_order_status(order.id,OrderEnum.ASSIGNED, time, rider.id)
        return res

    def assign_order_to_a_rider(self, order:Order, rider:Rider, time:int) -> bool:
        self.count += 1
        res = rider.add_order_destination(order, time)
        if res == True :
            self.success_count += 1
            order_simulator.change_order_status(order.id,OrderEnum.ASSIGNED, time, rider.id)
        return res
    
    def instance_simulate(self, index:int):
        self.riders[index].simulate(self.time)
        return self.riders[index]

    def get_unassigned_riders(self) -> List[Rider]:
        return self.unassigned_riders

    def simulate(self, time : int):
        for rider in self.riders:
            old_action = rider.current_action
            new_action = rider.simulate(time)
            if new_action != old_action:
                if new_action == ActionEnum.UNAVAILABLE:
                    if rider in self.unassigned_riders:
                        self.unassigned_riders.remove(rider)
                    if rider in self.working_riders:
                        self.working_riders.remove(rider)
                elif old_action == ActionEnum.NO_ACTION and rider in self.unassigned_riders:
                    self.unassigned_riders.remove(rider)
                elif new_action == ActionEnum.NO_ACTION:
                    self.unassigned_riders.append(rider)
                    if old_action == ActionEnum.UNAVAILABLE:
                        self.working_riders.append(rider)
                elif new_action == ActionEnum.RESTING and rider in self.unassigned_riders:
                    self.unassigned_riders.remove(rider)
                
        return True

    def export_log_file(self):
        print("[LOG] EXPORT RIDER LOCATION LOG FILE")
        location_log = list()
        for rider in self.riders:
            location_log.extend(rider.location_log)
        location_log_df = pd.DataFrame(location_log, columns=['id', 'time', 'action', 'lat', 'lng'])
        location_log_df.to_csv("{}/{}".format(Config.LOG_DIR, Config.RIDER_LOCATION_LOG_FILENAME), index=False)
        
        print("[LOG] EXPORT RIDER DESTINATION LOG FILE")
        destination_log = list()
        for rider in self.riders:
            destination_log.extend(rider.destination_log)
        destination_log_df = pd.DataFrame(destination_log, columns=['id', 'time', 'destination_type', 'lat', 'lng', 'order_id'])
        destination_log_df.to_csv("{}/{}".format(Config.LOG_DIR, Config.RIDER_DESTINATION_LOG_FILENAME), index=False)
            
rider_simulator = RiderSimulator()
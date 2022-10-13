from argparse import Action
from typing import Dict, List
from rider.rider import Rider, Order
#from order.order_simulator import Order
from common.action import ActionEnum

class RiderSimulator():
    def __init__(self):
        self.maximum_of_rider: int 
        self.maximum_order_per_rider: int 
        self.maximum_item_per_rider: int 
        self.riders : List[Rider] = list()
        self.working_riders : List[Rider] = list()
        self.unassigned_riders : List[Rider] = list() # ว่างงาน และต้อง Working ด้วย
        self.time = 0

    def create_rider_innitial_location(self, starting_time = 420, getoff_time = 1020):
        rider = Rider(id = len(self.riders), starting_time = starting_time, getoff_time = getoff_time)
        self.riders.append(rider)
        return rider

    def assign_order_to_a_rider(self, order:Order, rider:Rider, time:int) -> bool:
        rider.add_order_destination(order, time)
        return True
    
    def instance_simulate(self, index:int):
        self.riders[index].simulate(self.time)
        return self.riders[index]

    def get_unassigned_riders(self) -> List[Rider]:
        return self.unassigned_riders

    def simulate(self, time : int):
        for rider in self.riders:
            old_action = rider.current_action.action
            new_action = rider.simulate(time)
            if new_action != old_action:
                if new_action == ActionEnum.UNAVAILABLE:
                    if rider in self.unassigned_riders:
                        self.unassigned_riders.remove(rider)
                    self.working_riders.remove(rider)
                elif old_action == ActionEnum.NO_ACTION:
                    self.unassigned_riders.remove(rider)
                elif new_action == ActionEnum.NO_ACTION:
                    self.unassigned_riders.append(rider)
                    if old_action == ActionEnum.UNAVAILABLE:
                        self.working_riders.append(rider)
                elif new_action == ActionEnum.RESTING:
                    self.unassigned_riders.remove(rider)
                
        return True
            

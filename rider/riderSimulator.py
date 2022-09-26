from typing import Dict, List
from rider.rider import Rider
from order.order_simulator import Order
from type_enum.action import ActionEnum

class RiderSimulator():
    def __init__(self):
        self.maximum_of_rider: int 
        self.maximum_order_per_rider: int 
        self.maximum_item_per_rider: int 
        self.riders : List[Rider] = list()
        self.working_riders : List[Rider] = list()
        self.unassigned_riders : List[Rider] = list() # ว่างงาน และต้อง Working ด้วย
        self.time = 0

        #Mock up rider summoning
        for _ in range(100):
            rider = self.create_rider_innitial_location()
            if rider.status == ActionEnum.NO_ACTION:
                self.unassigned_riders.append(rider)
                self.working_riders.append(rider)

    def create_rider_innitial_location(self):
        rider = Rider(id = len(self.riders))
        self.riders.append(rider)
        return rider

    def assign_order_to_a_rider(self, order:Order, rider:Rider) -> bool:
        rider.add_order_destination(order)
        return True
    
    def instance_simulate(self, index:int):
        self.riders[index].simulate(self.time)
        return self.riders[index]

    def get_unassigned_riders(self) -> List[Rider]:
        return self.unassigned_riders

    def simulate(self, time : int):
        for rider in self.riders:
            old_status = rider.status
            new_status = rider.simulate(time)
            if new_status != old_status:
                if old_status == ActionEnum.NO_ACTION:
                    self.unassigned_riders.remove(rider)
                elif new_status == ActionEnum.NO_ACTION and len(rider.destinations) == 0:
                    self.unassigned_riders.append(rider)
                elif new_status == ActionEnum.UNAVAILABLE:
                    self.unassigned_riders.remove(rider)
                    self.working_riders.remove(rider)
                elif new_status == ActionEnum.RESTING:
                    self.unassigned_riders.remove(rider)
                
        return True
            

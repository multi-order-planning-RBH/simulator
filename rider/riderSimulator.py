from os import cpu_count
from typing import List
from rider import TempOrder, Rider

def parallelized_simulate(riders : List[Rider], time:int):
    for rider in riders:
        rider.simulate(time)
    return riders

class RiderSimulator():
    def __init__(self, processer : int = cpu_count()):
        self.maximumOfRider: int 
        self.maximumOrderPerRider: int 
        self.maximumItemPerRider: int 
        self.riders : List[Rider] = list()
        self.processer = processer
        self.time = 0

    def create_rider_innitial_location(self):
        rider = Rider(id = len(self.riders))
        self.riders.append(rider)

    def assign_order_to_a_rider(self, order:TempOrder, rider:Rider):
        rider.add_order_destination(order)
    
    def instance_simulate(self, index:int):
        self.riders[index].simulate(self.time)
        return self.riders[index]

    def simulate(self, time : int):
        for rider in self.riders:
            rider.simulate(time)
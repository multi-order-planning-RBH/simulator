from argparse import Action
from typing import List
import random
import sys, os
from restaurant.restaurant_simulator import Restaurant

from type_enum.order import OrderEnum
sys.path.append(os.path.abspath("./"))
from type_enum.location import LocationType, LocationEnum, generateBangkokLocation
from type_enum.action import ActionEnum
from type_enum.status import StatusEnum
from order.order_simulator import Order
from estimator import getEstimatedTimeTraveling

class Destination :
    def __init__(self, location : LocationType, type : LocationEnum, readyTime : int, order : Order):
        self.location : LocationType = location
        self.type : LocationEnum = type
        self.readyTime : int = readyTime
        self.order : Order = order
    
    def pick_up_or_deliver(self):
        if self.type == LocationEnum.RESTAURANT:
            self.order.status = OrderEnum.PICKED_UP
        elif self.type == LocationEnum.CUSTOMER:
            self.order.status = OrderEnum.DELIVERED

class Action : 
    def __init__(self, action : ActionEnum, location : LocationType, time : int):
        self.action : ActionEnum = action 
        self.location : LocationType = location 
        self.time : int = time 

class Rider:
    def __init__(self, id:int, starting_time:int = 0, getoff_time:int = 480, resting_time:int = 30):
        self.id : int = id
        self.location : LocationType = generateBangkokLocation()
        self.starting_time : int = starting_time
        self.getoff_time : int = getoff_time
        self.resting_time : int = resting_time
        self.resting_prob : float = 0.01
        self.destinations : List[Destination] = list()
        self.next_action : Action = None 
        self.status : StatusEnum = StatusEnum.WORKING
        self.current_action : Action = Action(ActionEnum.NO_ACTION, self.location, 0)
        #self.log : 
        self.speed : float = 0

    def add_order_destination(self, order : Order) -> bool:
        if self.current_action != ActionEnum.RESTING:
            self.destinations.append(Destination(order.resraurant_location, LocationEnum.RESTAURANT, order.ready_time))
            # May change 5 to be other number for randomness
            self.destinations.append(Destination(order.destination, LocationEnum.CUSTOMER, 5)) 
            return True
        return False

    def simulate(self, time : int) -> ActionEnum:
        if self.next_action == None:
            if self.current_action.action == ActionEnum.NO_ACTION and len(self.destinations) > 0: 
                next_action = ActionEnum.RIDING
                location = self.destinations[0].location
                next_time = time + 1
                self.next_action = Action(next_action, location, next_time)
            elif random.uniform(0, 1)<self.resting_prob: 
                next_action = ActionEnum.RESTING
                location = self.location
                next_time = time + 1
                self.next_action = Action(next_action, location, next_time)

        elif time >= self.next_action.time : 
            self.current_action = self.next_action
            self.location = self.current_action.location if self.current_action != None else self.location
            
            if self.current_action.action == ActionEnum.RIDING:
                next_action = ActionEnum.WAITING
                location = self.current_action.location
                next_time = time + getEstimatedTimeTraveling()
                self.next_action = Action(next_action, location, next_time)

            elif self.current_action.action == ActionEnum.WAITING:
                next_action = ActionEnum.PICKUP_OR_DELIVER
                location = self.current_action.location
                destination = self.destinations[0]
                ready_time = destination.readyTime 

                #Add additional time for waiting customer to come for pick up the order when riding to the customer
                ready_time += 0 if destination.type == LocationEnum.RESTAURANT else time

                #Compare waiting time and commuting time
                next_time = max(ready_time, self.current_action.time)+1

                self.next_action = Action(next_action, location, next_time)

            elif self.current_action.action == ActionEnum.PICKUP_OR_DELIVER:
                destination = self.destinations[0]
                destination.pick_up_or_deliver()
                self.destinations.pop(0)
                if len(self.destinations) == 0:
                    next_action = ActionEnum.NO_ACTION
                    location = self.location
                    self.next_action = Action(next_action, location, next_time)
                else:
                    next_action = ActionEnum.RIDING
                    location = self.destinations[0].location
                next_time = time + 1
                self.next_action = Action(next_action, location, next_time)

            
            elif self.current_action.action == ActionEnum.RESTING :
                next_action = ActionEnum.NO_ACTION
                location = self.location
                next_time = time + self.resting_time
                self.next_action = Action(next_action, location, next_time)
            
            elif self.current_action.action == ActionEnum.NO_ACTION :
                self.next_action = None
            
        return self.current_action

        


from argparse import Action
from typing import List
import random
import sys, os

from type_enum.order import OrderEnum
sys.path.append(os.path.abspath("./"))
from type_enum.location import Coordinates, LocationEnum, generateBangkokLocation_2
from type_enum.action import ActionEnum
from type_enum.status import StatusEnum
from order.order_simulator import Order
from estimator import getEstimatedTimeTraveling

class Destination :
    def __init__(self, location : Coordinates, type : LocationEnum, readyTime : int, order : Order):
        self.location : Coordinates = location
        self.type : LocationEnum = type
        self.readyTime : int = readyTime
        self.order : Order = order
    
    def pick_up_or_deliver(self):
        if self.type == LocationEnum.RESTAURANT:
            self.order.status = OrderEnum.PICKED_UP
        elif self.type == LocationEnum.CUSTOMER:
            self.order.status = OrderEnum.DELIVERED

class Action : 
    def __init__(self, action : ActionEnum, time : int):
        self.action : ActionEnum = action 
        self.time : int = time 

class Rider:
    def __init__(self, id:int, starting_time:int = 0, getoff_time:int = 480, resting_time:int = 30):
        self.id : int = id
        self.location : Coordinates = generateBangkokLocation_2()
        self.starting_time : int = starting_time
        self.getoff_time : int = getoff_time
        self.resting_time : int = resting_time
        self.resting_prob : float = 0.01
        self.destinations : List[Destination] = list()
        self.next_action : Action = None 
        self.status : StatusEnum = StatusEnum.WORKING
        if starting_time == 0:
            self.current_action : Action = Action(ActionEnum.NO_ACTION, self.location, 0)
        else :
            self.current_action : Action = Action(ActionEnum.UNAVAILABLE, self.location, 0)
            self.next_action : Action = Action(ActionEnum.NO_ACTION, self.location, starting_time)
        #self.log : 
        self.speed : Coordinates = Coordinates()

    def add_order_destination(self, order : Order, time : int) -> bool:
        if self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE or \
            self.getoff_time - time < 1800:
            self.destinations.append(Destination(order.resraurant_location, LocationEnum.RESTAURANT, order.ready_time))
            # May change 5 to be other number for randomness
            self.destinations.append(Destination(order.destination, LocationEnum.CUSTOMER, 5)) 
            return True
        return False

    def calculate_speed(self, destination : Coordinates, traveling_time : int):
        self.speed = (destination - self.location)/traveling_time

    def simulate(self, time : int) -> ActionEnum:
        if self.next_action == None:
            if self.current_action.action == ActionEnum.NO_ACTION and len(self.destinations) > 0: 
                next_action = ActionEnum.RIDING
                next_time = time + 1
                self.next_action = Action(next_action, next_time)
            elif random.uniform(0, 1)<self.resting_prob: 
                next_action = ActionEnum.RESTING
                next_time = time + 1
                self.next_action = Action(next_action, next_time)

        elif time >= self.next_action.time : 
            self.location += self.speed
            self.current_action = self.next_action
            
            if self.current_action.action == ActionEnum.RIDING:
                self.calculate_speed()
                next_action = ActionEnum.WAITING
                next_time = time + getEstimatedTimeTraveling()
                self.next_action = Action(next_action, next_time)

            elif self.current_action.action == ActionEnum.WAITING:
                self.speed = Coordinates()
                next_action = ActionEnum.PICKUP_OR_DELIVER
                destination = self.destinations[0]
                ready_time = destination.readyTime 

                #Add additional time for waiting customer to come for pick up the order when riding to the customer
                ready_time += 0 if destination.type == LocationEnum.RESTAURANT else time

                #Compare waiting time and commuting time
                next_time = max(ready_time, self.current_action.time)+1

                self.next_action = Action(next_action, next_time)

            elif self.current_action.action == ActionEnum.PICKUP_OR_DELIVER:
                self.speed = Coordinates()
                destination = self.destinations[0]
                destination.pick_up_or_deliver()
                self.destinations.pop(0)
                if len(self.destinations) == 0:
                    next_action = ActionEnum.NO_ACTION
                    self.next_action = Action(next_action, next_time)
                else:
                    next_action = ActionEnum.RIDING
                next_time = time + 1
                self.next_action = Action(next_action, next_time)

            
            elif self.current_action.action == ActionEnum.RESTING :
                self.speed = Coordinates()
                next_action = ActionEnum.NO_ACTION
                next_time = time + self.resting_time
                self.next_action = Action(next_action, next_time)
            
            elif self.current_action.action == ActionEnum.NO_ACTION :
                self.speed = Coordinates()
                self.next_action = None
            
        return self.current_action

        


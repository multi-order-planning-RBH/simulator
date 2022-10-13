from argparse import Action
from typing import Dict, List
import random
import sys, os
sys.path.append(os.path.abspath("./"))
from common.order import OrderEnum
from common.location import Coordinates, LocationEnum, generateBangkokLocation_2
from common.action import ActionEnum
from common.status import StatusEnum
#from order.order_simulator import Order
from rider.estimator import getEstimatedTimeTraveling

class Order:

    def __init__(self, destination,resraurant_location,order_idx,created_time,ready_time):
        self.id = order_idx
        self.resraurant_location = resraurant_location
        self.destination = destination
        self.created_time = created_time
        self.ready_time = ready_time
        self.status = "Created"
        self.rider=None

        #Complete order 
        #self.finish_time 


class Destination :
    def __init__(self, order : Order, location : Coordinates, type : LocationEnum, readyTime : int):
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
            self.current_action : Action = Action(ActionEnum.NO_ACTION, 0)
        else :
            self.current_action : Action = Action(ActionEnum.UNAVAILABLE, 0)
            self.next_action : Action = Action(ActionEnum.NO_ACTION, starting_time)
        self.log : Dict[int, list] = dict()
        self.speed : Coordinates = Coordinates()
        self.utilization_time : int = 0
        self.working_time : int = self.getoff_time - self.starting_time
        self.current_destination : Destination = None

    def add_order_destination(self, order : Order, time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 30:
            self.destinations.append(Destination(order, order.resraurant_location, LocationEnum.RESTAURANT, order.ready_time))
            # May change 5 to be other number for randomness
            self.destinations.append(Destination(order, order.destination, LocationEnum.CUSTOMER, 5)) 
            return True
        return False

    def calculate_speed(self, traveling_time : int):
        destination = self.destinations[0].location
        self.speed = (destination - self.location)/traveling_time

    def logging(self, time):
        action = self.current_action.time
        if len(self.destinations) > 0:
            destination_x = self.destinations[0].location.x
            destination_y = self.destinations[0].location.y
        else :
            destination_x = destination_y = None
        temp = [time, action, destination_x, destination_y]
        self.log[time] = temp

    def simulate(self, time : int) -> ActionEnum:
        self.location += self.speed
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
            self.current_action = self.next_action
            self.logging(time)
            
            if self.current_action.action == ActionEnum.RIDING:
                next_action = ActionEnum.WAITING
                next_time = getEstimatedTimeTraveling()
                self.calculate_speed(next_time)
                self.current_destination = self.destinations.pop(0)
                self.utilization_time += next_time
                next_time += time
                self.next_action = Action(next_action, next_time)

            elif self.current_action.action == ActionEnum.WAITING:
                self.speed = Coordinates()
                next_action = ActionEnum.PICKUP_OR_DELIVER
                destination = self.current_destination
                ready_time = destination.readyTime 

                #Add additional time for waiting customer to come for pick up the order when riding to the customer
                ready_time += 0 if destination.type == LocationEnum.RESTAURANT else time

                #Compare waiting time and commuting time
                next_time = max(ready_time, self.current_action.time)+1

                self.next_action = Action(next_action, next_time)

            elif self.current_action.action == ActionEnum.PICKUP_OR_DELIVER:
                self.speed = Coordinates()
                self.current_destination.pick_up_or_deliver()
                if len(self.destinations) == 0:
                    next_action = ActionEnum.NO_ACTION
                else:
                    next_action = ActionEnum.RIDING
                next_time = time + 1
                self.next_action = Action(next_action, next_time)

            
            elif self.current_action.action == ActionEnum.RESTING :
                self.speed = Coordinates()
                self.current_destination = None
                next_action = ActionEnum.NO_ACTION
                next_time = time + self.resting_time
                self.next_action = Action(next_action, next_time)
            
            elif self.current_action.action == ActionEnum.NO_ACTION :
                self.speed = Coordinates()
                self.current_destination = None
                self.next_action = None
        
        #Need to concern about remaining order
        if time >= self.getoff_time:
            self.current_destination = None
            next_action = ActionEnum.UNAVAILABLE
            next_time = time+1
            self.current_action = Action(next_action, next_time)
            self.next_action = None
            
        return self.current_action.action

        


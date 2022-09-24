from argparse import Action
from typing import List
import random
import sys, os
sys.path.append(os.path.abspath("./"))
from type_enum.location import LocationType, LocationEnum, generateBangkokLocation
from type_enum.action import ActionEnum
from type_enum.status import StatusEnum
from estimator import getEstimatedTimeTraveling

class TempOrder:
    def __init__(self, resraurantLocation, destination, orderTime, readyTime):
        self.resraurantLocation = resraurantLocation
        self.destination = destination
        self.orderTime = orderTime
        self.readyTime = readyTime

class Destination :
    def __init__(self, location : LocationType, type : LocationEnum, readyTime : int):
        self.location : LocationType = location
        self.type : LocationEnum = type
        self.readyTime : int = readyTime

class Action : 
    def __init__(self, action : ActionEnum, location : LocationType, time : int):
        self.action : ActionEnum = action 
        self.location : LocationType = location 
        self.time : int = time 

class Rider:
    def __init__(self, id:int, startingTime:int = 0, getoffTime:int = 480, restingTime:int = 30):
        self.id : int = id
        self.location : LocationType = generateBangkokLocation()
        self.startingTime : int = startingTime
        self.getoffTime : int = getoffTime
        self.restingTime : int = restingTime
        self.restingProb : float = 0.01
        self.destinations : List[Destination] = list()
        self.nextAction : Action = None 
        self.status : StatusEnum = StatusEnum.WORKING
        self.currentAction : Action = Action(ActionEnum.NO_ACTION, self.location, 0)
        #self.log : 
        self.speed : float = 0

    def add_order_destination(self, order : TempOrder) -> bool:
        if self.currentAction != ActionEnum.RESTING:
            self.destinations.append(Destination(order.resraurantLocation, LocationEnum.RESTAURANT, order.readyTime))
            # May change 5 to be other number for randomness
            self.destinations.append(Destination(order.destination, LocationEnum.CUSTOMER, 5)) 
            return True
        return False

    def simulate(self, time : int) -> ActionEnum:
        if self.nextAction == None:
            if self.currentAction.action == ActionEnum.NO_ACTION and len(self.destinations) > 0: 
                next_action = ActionEnum.RIDING
                location = self.destinations[0].location
                next_time = time + 1
                self.nextAction = Action(next_action, location, next_time)
            elif random.uniform(0, 1)<self.restingProb: 
                next_action = ActionEnum.RESTING
                location = self.location
                next_time = time + 1
                self.nextAction = Action(next_action, location, next_time)

        elif time >= self.nextAction.time : 
            self.currentAction = self.nextAction
            self.location = self.currentAction.location if self.currentAction != None else self.location
            
            if self.currentAction.action == ActionEnum.RIDING:
                next_action = ActionEnum.WAITING
                location = self.currentAction.location
                next_time = time + getEstimatedTimeTraveling()
                self.nextAction = Action(next_action, location, next_time)

            elif self.currentAction.action == ActionEnum.WAITING:
                next_action = ActionEnum.PICKUP_OR_DELIVER
                location = self.currentAction.location
                destination = self.destinations[0]
                ready_time = destination.readyTime 

                #Add additional time for waiting customer to come for pick up the order when riding to the customer
                ready_time += 0 if destination.type == LocationEnum.RESTAURANT else time

                #Compare waiting time and commuting time
                next_time = max(ready_time, self.currentAction.time)+1

                self.nextAction = Action(next_action, location, next_time)

            elif self.currentAction.action == ActionEnum.PICKUP_OR_DELIVER:
                self.destinations.pop(0)
                next_action = ActionEnum.NO_ACTION
                location = self.location
                next_time = time + 1
                self.nextAction = Action(next_action, location, next_time)
            
            elif self.currentAction.action == ActionEnum.RESTING :
                next_action = ActionEnum.NO_ACTION
                location = self.location
                next_time = time + self.restingTime
                self.nextAction = Action(next_action, location, next_time)
            
            elif self.currentAction.action == ActionEnum.NO_ACTION :
                self.nextAction = None
            
        return self.currentAction

        


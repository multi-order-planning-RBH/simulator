from argparse import Action
from typing import List

from type_enum.location import LocationType, LocationEnum, generateBangkokLocation
from type_enum.action import ActionEnum
from type_enum.status import StatusEnum
from estimator import getEstimatedTimeTraveling

class TempOrder:
    resraurantLocation : LocationType = [13.744740, 100.531876]
    destination : LocationType = [13.741291, 100.528645]
    orderTime = 0
    readyTime = 30

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
    def __init__(self, id:int, startingTime = 0, getoffTime = 480, restingTime = 30):
        self.id : int = id
        self.location : LocationType = generateBangkokLocation()
        self.startingTime : int = startingTime
        self.getoffTime : int = getoffTime
        self.restingTime : int = restingTime
        self.destinations : List[Destination] = list()
        self.nextAction : Action = None 
        self.status : StatusEnum = StatusEnum.WORKING
        self.currentAction : Action = Action(ActionEnum.NO_ACTION, self.location, 0)
        #self.log : 
        self.speed : float = 0

    def add_order_destination(self, order : TempOrder):
        self.destinations.append(Destination(order.resraurantLocation, LocationEnum.RESTAURANT, order.readyTime))
        
        # May change 5 to be other number for randomness
        self.destinations.append(Destination(order.destination, LocationEnum.CUSTOMER, 5)) 

    def simulate(self, time):
        if self.currentAction.action == ActionEnum.NO_ACTION:
                if len(self.destinations)>0:
                    next_action = ActionEnum.RIDING
                    location = self.destinations[0].location
                    next_time += 1
                    self.nextAction = Action(next_action, location, next_time)
        if self.nextAction.time >= time : 
            self.currentAction = self.nextAction
            
            if self.currentAction.action == ActionEnum.RIDING:
                next_action = ActionEnum.WAITING
                location = self.currentAction.location
                next_time += getEstimatedTimeTraveling()
                self.nextAction = Action(next_action, location, next_time)

            elif self.currentAction.action == ActionEnum.WAITING:
                next_action = ActionEnum.PICKUP_OR_DELIVER
                location = self.currentAction.location
                destination = self.destinations[0]
                ready_time = destination.readyTime 

                #Add extension time for waiting customer to come for pick up the order when riding to the customer
                ready_time += 0 if destination.type == LocationEnum.RESTAURANT else time

                #Compare waiting time and commuting time
                next_time = max(ready_time, self.currentAction.time)

                self.nextAction = Action(next_action, location, next_time)

            elif self.currentAction.action == ActionEnum.PICKUP_OR_DELIVER:
                self.destinations.pop()
                next_action = ActionEnum.NO_ACTION
                location = self.location
                next_time += 1
                self.nextAction = Action(next_action, location, next_time)

        


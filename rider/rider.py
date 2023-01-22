import random
import sys, os

from argparse import Action
from typing import Dict, List
from math import ceil
from shapely import Point

sys.path.append(os.path.abspath("./"))

from common.location import LocationEnum
from common.action import ActionEnum
from common.status import StatusEnum
from order_restaurant.order_restaurant_simulator import Order, Destination
from suggester.types.batch import Batch
from map.map import get_geometry_of_path
from config import Config


class Action : 
    def __init__(self, action : ActionEnum, time : int):
        self.action : ActionEnum = action 
        self.time : int = time 

class Rider:
    def __init__(self, id:int, location:Point, starting_time:int = 0, getoff_time:int = 480, resting_time:int = 30):
        self.id : int = id
        self.location : Point = location
        self.starting_time : int = starting_time
        self.getoff_time : int = getoff_time
        self.resting_time : int = resting_time
        self.resting_prob : float = 0.01
        self.destinations : List[Destination] = list()
        self.next_action : Action = None 
        self.status : StatusEnum = StatusEnum.WORKING

        self.current_action : ActionEnum = ActionEnum.NO_ACTION
        self.done_current_action_time : int = 0
        if starting_time != 0 :
            self.current_action = ActionEnum.UNAVAILABLE
            self.done_current_action_time = starting_time

        self.log : Dict[int, list] = dict()
        self.speed : float = Config.RIDER_SPEED
        self.working_time : int = self.getoff_time - self.starting_time
        self.current_destination : Destination = None
        self.order_count : int = 0

        self.path = None
        self.time_traveling = 0
        self.t = 0

    def add_order_destination(self, order : Order, time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 1800:

            self.order_count += 1
            
            # self.destinations.append(Destination(order, order.restaurant_location, LocationEnum.RESTAURANT, order.cooking_duration))
            self.destinations.append(order.restaurant_destination)
            # May change 5 to be other number for randomness
            self.destinations.append(order.customer_destination) 

            return True
        return False

    # batch mode
    def add_batch_destination(self, batch : Batch, time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 1800:

            self.order_count += len(batch.orders)
            
            self.destinations+=batch.destinations

            return True
        return False

    # online mode
    def add_online_destination(self, batch : Batch, time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 1800:
            return False
        return False

    # def calculate_speed(self, traveling_time : int):
    #     destination = self.destinations[0].location
    #     self.speed = (destination - self.location)/traveling_time

    def logging(self, time):
        action = self.current_action
        location_x = self.location.x
        location_y = self.location.x
        temp = [time, action, location_x, location_y]
        self.log[time] = temp

    def simulate(self, time : int) -> ActionEnum:
        if time % Config.RIDER_LOGGING_PERIOD == 0:
            self.logging(time)

        if self.current_action == ActionEnum.NO_ACTION:
            if len(self.destinations) > 0:
                self.current_action = ActionEnum.RIDING
                # Need to specify
                origin = self.location
                dest = self.destinations[0].location
                self.path = get_geometry_of_path(origin, dest)
                self.time_traveling = ceil(self.path.length/self.speed)
                self.t = 1

            elif random.uniform(0, 1)<self.resting_prob: 
                self.current_action = ActionEnum.RESTING
                self.done_current_action_time = time + self.resting_time

        elif self.current_action == ActionEnum.RIDING:
            self.location = self.path.interpolate(self.speed*self.t)
            self.t += 1
            if self.t > self.time_traveling:
                self.current_action = ActionEnum.WAITING
                destination = self.current_destination
                order = destination.order
                if order and destination.type == LocationEnum.RESTAURANT:
                    self.done_current_action_time = order.meal_finished_time
                else : 
                    self.done_current_action_time = time

        elif self.current_action == ActionEnum.WAITING:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.ACTION

        elif self.current_action == ActionEnum.ACTION:
            self.current_destination.action(time)
            self.current_action = ActionEnum.NO_ACTION

        elif self.current_action == ActionEnum.RESTING:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.NO_ACTION
        
        elif self.current_action == ActionEnum.UNAVAILABLE:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.NO_ACTION

        else:
            pass

        # if time >= self.getoff_time:
        #     self.current_destination = None
        #     self.current_action = ActionEnum.GETOFF 
            
        return self.current_action

        


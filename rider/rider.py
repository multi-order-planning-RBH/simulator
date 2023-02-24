import random
import sys, os

from argparse import Action
from typing import Dict, List
from math import ceil
from shapely import Point

sys.path.append(os.path.abspath("./"))

from common.location import LocationEnum
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, Destination
from suggester.types.batch import Batch
from map.map import get_geometry_of_path
from config import Config
from pyproj import Geod
from scipy.stats import truncnorm

class Action : 
    def __init__(self, action : ActionEnum, time : int):
        self.action : ActionEnum = action 
        self.time : int = time 

class Rider:
    def __init__(self, id:int, location:Point, starting_time:int = 0, getoff_time:int = 480, resting_time:int = 30):
        self.id : int = id
        self.location : Point = location
        self.path = None

        self.starting_time : int = starting_time
        self.getoff_time : int = getoff_time
        self.resting_time : int = resting_time
        self.resting_prob : float = 0.01
    

        self.current_action : ActionEnum = ActionEnum.NO_ACTION
        self.done_current_action_time : int = 0
        if starting_time != 0 :
            self.current_action = ActionEnum.UNAVAILABLE
            self.done_current_action_time = starting_time

        self.log : Dict[int, list] = dict()
        self.speed : float = truncnorm.rvs((Config.RIDER_SPEED_LOWER_BOUND - Config.RIDER_SPEED_MEAN) / Config.RIDER_SPEED_STD, 
                                            (Config.RIDER_SPEED_UPPER_BOUND - Config.RIDER_SPEED_MEAN) / Config.RIDER_SPEED_STD,    
                                            loc=Config.RIDER_SPEED_MEAN, 
                                            scale=Config.RIDER_SPEED_STD, 
                                            size=1)[0]

        self.destinations : List[Destination] = list()
        self.current_destination : Destination = None

        self.order_count : int = 0
        self.cum_order_count : int = 0

        self.current_traveling_time = 0
        self.current_traveling_time = 0
        self.utilization_time = 0
        self.t = 0

    def add_order_destination(self, order : Order, time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 1800:

            self.order_count += 1
            self.cum_order_count += 1
            
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
            self.cum_order_count += len(batch.orders)
            
            self.destinations+=batch.destinations

            return True
        return False

    # online mode
    def add_online_destination(self, order: Order, destinations: List[Destination], time : int) -> bool:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) and \
            self.getoff_time - time > 1800:

            self.order_count += 1
            self.cum_order_count += 1
            self.destinations = destinations
            return True
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
                self.current_destination = self.destinations.pop(0)

                origin = self.location
                dest = self.current_destination.location
                self.path = get_geometry_of_path(origin, dest)

                length_meters = Geod(ellps="WGS84").geometry_length(self.path)

                self.current_traveling_time = ceil(length_meters/self.speed)
                self.t = 1

            elif random.uniform(0, 1)<self.resting_prob: 
                self.current_action = ActionEnum.RESTING
                self.done_current_action_time = time + self.resting_time

        elif self.current_action == ActionEnum.RIDING:
            self.utilization_time += 1
            self.location = self.path.interpolate(self.speed*self.t)
            self.t += 1
            if self.t > self.current_traveling_time:
                self.current_action = ActionEnum.WAITING
                destination = self.current_destination
                if destination:
                    order = destination.order
                    if order and destination.type == LocationEnum.RESTAURANT:
                        self.done_current_action_time = order.meal_finished_time
                    else : 
                        self.done_current_action_time = time

        elif self.current_action == ActionEnum.WAITING:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.ACTION

        elif self.current_action == ActionEnum.ACTION:
            destination = self.current_destination
            if destination:
                destination.action(time)
                if destination.type == LocationEnum.CUSTOMER:
                        self.order_count -= 1
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

        


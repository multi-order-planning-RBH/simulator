import random

from typing import List
from math import ceil
from shapely import Point
from pyproj import Geod
from scipy.stats import truncnorm

from common.location import LocationEnum
from common.action import ActionEnum
from order_restaurant.order_restaurant_simulator import Order, Destination
from suggester.types.batch import Batch
from map.map import get_geometry_of_path , sample_uniform_restaurant_location
from config import Config

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

        self.log : dict = dict()
        self.speed : float = sample_rider_speed()

        self.destinations : List[Destination] = list()
        self.current_destination : Destination = None

        self.order_count : int = 0
        self.cum_order_count : int = 0

        self.traveling_time = 0
        self.utilization_time = 0
        self.t = 0

        self.location_log = list()
        self.destination_log = list()

    def add_order_destination(self, order : Order, time : int) -> bool:
        # if (self.current_action != ActionEnum.RESTING or \
        #     self.current_action != ActionEnum.UNAVAILABLE) and \
        #     self.getoff_time - time > 1800:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) :

            self.check_riding_back_status_after_assignment()
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
        # if (self.current_action != ActionEnum.RESTING or \
        #     self.current_action != ActionEnum.UNAVAILABLE) and \
        #     self.getoff_time - time > 1800:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) :

            self.check_riding_back_status_after_assignment()
            self.order_count += len(batch.orders)
            self.cum_order_count += len(batch.orders)
            
            self.destinations+=batch.destinations

            return True
        return False

    # online mode
    def add_online_destination(self, order: Order, destinations: List[Destination], time : int) -> bool:
        # if (self.current_action != ActionEnum.RESTING or \
        #     self.current_action != ActionEnum.UNAVAILABLE) and \
        #     self.getoff_time - time > 1800:
        if (self.current_action != ActionEnum.RESTING or \
            self.current_action != ActionEnum.UNAVAILABLE) :

            self.check_riding_back_status_after_assignment()
            self.order_count += 1
            self.cum_order_count += 1
            self.destinations = destinations
            return True
        return False

    # def calculate_speed(self, traveling_time : int):
    #     destination = self.destinations[0].location
    #     self.speed = (destination - self.location)/traveling_time

    def check_riding_back_status_after_assignment(self):
        if self.current_action == ActionEnum.RIDING_BACK_TO_RESTAURANT_AREA:
            self.current_action = ActionEnum.NO_ACTION

    def logging(self, time):
        action = self.current_action
        location_x = self.location.x
        location_y = self.location.y
        temp = [self.id, time, action, location_y, location_x]
        self.location_log.append(temp)

        if self.current_destination:
            current_destination = self.current_destination
            temp = [[   self.id, time, current_destination.type, current_destination.location.y,\
                        current_destination.location.x, current_destination.order.id]]
            for d in self.destinations:
                temp_destination_log = [self.id, time, d.type, d.location.y, d.location.x, d.order.id]
                temp.append(temp_destination_log)
            self.destination_log.extend(temp)

    def simulate(self, time : int) -> ActionEnum:
        if time % Config.RIDER_LOG_PERIOD == 0:
            self.logging(time)

        if self.current_action == ActionEnum.NO_ACTION:
            if len(self.destinations) > 0:
                self.current_action = ActionEnum.RIDING
                self.current_destination = self.destinations.pop(0)

                origin = self.location
                dest = self.current_destination.location
                self.speed = sample_rider_speed()
                self.traveling_time, self.path = compute_traveling_time_and_path(origin, dest, self.speed)
                self.done_current_action_time = time + self.traveling_time

                # self.path = get_geometry_of_path(origin, dest)
                # length_meters = Geod(ellps="WGS84").geometry_length(self.path)
                # self.current_traveling_time = ceil(length_meters/self.speed)

                self.t = 1

            elif random.uniform(0, 1)<self.resting_prob: 
                self.current_action = ActionEnum.RESTING
                self.done_current_action_time = time + self.resting_time

        elif self.current_action == ActionEnum.RIDING:
            self.utilization_time += 1
            if self.traveling_time!=0:
                self.location = self.path.interpolate(self.t/self.traveling_time, normalized=True)
            self.t += 1
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.WAITING
                destination = self.current_destination
                if destination:
                    order = destination.order
                    if order and destination.type == LocationEnum.RESTAURANT:
                        self.done_current_action_time = order.meal_finished_time
                    else : 
                        self.done_current_action_time = time
                else:
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
                if len(self.destinations) > 0:
                    self.current_action = ActionEnum.NO_ACTION
                else:
                    self.current_action = ActionEnum.RIDING_BACK_TO_RESTAURANT_AREA
                    origin = self.location
                    dest = sample_uniform_restaurant_location()
                    self.speed = sample_rider_speed()
                    self.traveling_time, self.path = compute_traveling_time_and_path(origin, dest, self.speed)
                    self.done_current_action_time = time + self.traveling_time
                    self.t = 1
            else:
                self.current_action = ActionEnum.NO_ACTION

        elif self.current_action == ActionEnum.RIDING_BACK_TO_RESTAURANT_AREA:
            if self.traveling_time!=0:
                self.location = self.path.interpolate(self.t/self.traveling_time, normalized=True)
            self.t += 1
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.NO_ACTION
                self.path = None

        elif self.current_action == ActionEnum.RESTING:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.NO_ACTION
        
        elif self.current_action == ActionEnum.UNAVAILABLE:
            if time > self.done_current_action_time:
                self.current_action = ActionEnum.NO_ACTION

        else:
            pass

            
        return self.current_action

    def __lt__(self,other):
        return True

        

def sample_rider_speed():
    return truncnorm.rvs((Config.RIDER_SPEED_LOWER_BOUND - Config.RIDER_SPEED_MEAN) / Config.RIDER_SPEED_STD, 
                                            (Config.RIDER_SPEED_UPPER_BOUND - Config.RIDER_SPEED_MEAN) / Config.RIDER_SPEED_STD,    
                                            loc=Config.RIDER_SPEED_MEAN, 
                                            scale=Config.RIDER_SPEED_STD, 
                                            size=1)[0]

def compute_traveling_time_and_path(origin, dest, speed):
    path = get_geometry_of_path(origin, dest)
    length_meters = Geod(ellps="WGS84").geometry_length(path)
    traveling_time = ceil(length_meters/speed)

    return traveling_time, path
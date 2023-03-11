import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath("..\\simulator"))

import scipy.stats
from shapely import Point
import random
from common.order import OrderEnum
from common.location import LocationEnum
from ml_estimator.cooking_duration import estimate_cooking_duration
from map.map import sample_uniform_bangkok_location

from config import Config
from common.system_logger import SystemLogger
logger = SystemLogger(__name__)

# from type_enum.order_status import OrderStatusEnum


class Restaurant:

    def __init__(self, location, restaurant_idx, mean=1000, std=300, order_rate=0.003):
        self.id: int = restaurant_idx
        self.location: Point = location
        # queue of orderId
        self.order_id_queue: list[int] = []
        self.mean: int = mean
        self.std: int = std
        self.order_rate: float = order_rate

    def rider_pickup_order(self, pickup_order):
        # check if pickup_order ready if yes
        # Pop pickup_order from order_queue
        #
        order_simulator.change_order_status(pickup_order.id, OrderEnum.DELIVERING)
        self.order_id_queue = [
            o_id for o_id in self.order_id_queue if o_id != pickup_order.id]

    def preparing_current_order(self, time):
        if len(self.order_id_queue) > 0:
            current_order = order_simulator.get_order_by_id(
                self.order_id_queue[0])
            if time >= current_order.cooking_duration and current_order.status == OrderEnum.ASSIGNED:
                # change status of order by order id
                order_simulator.change_order_status(
                    self.order_id_queue[0], OrderEnum.READY)

    def real_cooking_duration(self, order):
        # Estimate "Real" cooking Time from Gaussian
        # preparing time distribution.estimate sth like that

        if self.std == 0:
            self.std = 100

        lower_bound = 200
        upper_bound = 2500

        cooking_duration = int(scipy.stats.truncnorm.rvs((lower_bound-self.mean)/self.std,
                                                         (upper_bound -
                                                          self.mean)/self.std,
                                                         loc=self.mean, scale=self.std, size=1)[0])
        if cooking_duration <= 0:
            cooking_duration = 1000
        return cooking_duration


class RestaurantSimulator:
    def __init__(self):
        self.restaurant_idx: int = 0
        self.restaurant_list: list[Restaurant] = []
        self.restaurant_id_list: list[int] = []
        # res_list = pd.read_csv("order_restaurant/restaurant_sample.csv")
        # res_list = pd.read_csv("order_restaurant/restaurant_sample_10000.csv")
        res_list = pd.read_csv("order_restaurant/restaurant_sample_10000_w_rate.csv")
        for idx, res in res_list.iterrows():
            new_res = Restaurant(Point(res["Merchant.Lng"], res["Merchant.Lat"]),
                                 self.restaurant_idx, res["mean_preparing_time"], res["std_preparing_time"],
                                 res['num_job_per_sec'])
            self.restaurant_idx += 1
            self.restaurant_list.append(new_res)
            self.restaurant_id_list.append(idx)

    def simulate(self, time):

        # loop check each restaurant
        for res_id in range(len(self.restaurant_list)):
            res = self.restaurant_list[res_id]

            # complete current order
            res.preparing_current_order(time)

    def real_cooking_duration(self, restaurant_id, order):

        res_id = self.restaurant_id_list.index(restaurant_id)

        return self.restaurant_list[res_id].real_cooking_duration(order)

    def assign_order_to_restaurant(self, restaurant_id, order):

        res_id = self.restaurant_id_list.index(restaurant_id)

        self.restaurant_list[res_id].order_id_queue.append(order.id)

    def get_restaurant_by_id(self, res_id):
        try:
            idx = self.restaurant_id_list.index(res_id)
            return self.restaurant_list[idx]
        except:
            logger.warning(f"Restaurant with Id {res_id} is not found.")
            return None

    def get_all_restaurant_id(self):
        return self.restaurant_id_list


class Order:

    def __init__(self, restaurant_id, order_idx, created_time):
        self.id: int = order_idx
        self.restaurant: int = restaurant_id
        self.restaurant_destination: Destination = None
        self.customer_destination: Destination = None
        self.created_time: int = created_time
        self.assigned_time: int = None
        self.meal_finished_time: int = None
        self.picked_up_time: int = None
        self.cooking_duration: int = None
        self.estimated_cooking_duration: int = None
        self.finished_time: int = None
        self.status: OrderEnum = OrderEnum.CREATED
        self.rider_id = None


class OrderSimulator:

    def __init__(self):
        self.order_idx = 0
        self.order_dict = {}
        self.finished_order_list = []
        self.unassigned_order_list = []
        self.assigned_order_list = []
        self.cancelled_order_list = []

    def simulate(self, time):
        # num order should be randomed from some distribution
        cancelled_id = []
        for order in self.unassigned_order_list:
            # this can be params too
            if time - order.created_time > 600:
                self.cancelled_order_list.append(order)
                cancelled_id.append(order.id)

        self.unassigned_order_list = [
            o for o in self.unassigned_order_list if o.id not in cancelled_id]

        restaurant_list = restaurant_simulator.get_all_restaurant_id()
        for restaurant_id in restaurant_list:
            restaurant = restaurant_simulator.get_restaurant_by_id(restaurant_id)
            
            uniform_value = random.random()

            if uniform_value<restaurant.order_rate:


                customer_destination = sample_uniform_bangkok_location()
                self.create_order(customer_destination, restaurant_id, time)
                
    def create_order(self, customer_destination, restaurant_id, created_time):

        restaurant = restaurant_simulator.get_restaurant_by_id(restaurant_id)
        new_order = Order(restaurant_id, self.order_idx, created_time)
        new_order.cooking_duration = restaurant_simulator.real_cooking_duration(
            restaurant_id, new_order)
        new_order.estimated_cooking_duration = estimate_cooking_duration(
            new_order)

        new_order.restaurant_destination = Destination(
            new_order, restaurant.location, LocationEnum.RESTAURANT, new_order.cooking_duration, new_order.estimated_cooking_duration)
        new_order.customer_destination = Destination(
            new_order, customer_destination, LocationEnum.CUSTOMER, 5, 0)

        self.order_dict[self.order_idx] = new_order

        self.unassigned_order_list.append(new_order)

        restaurant_simulator.assign_order_to_restaurant(
            restaurant_id, new_order)

        self.order_idx += 1

    def change_order_status(self, order_id, status, time=0 ,rider_id=None):

        try:
            self.order_dict[order_id].status = status

            if status == OrderEnum.ASSIGNED:
                self.order_dict[order_id].assigned_time = time
                self.order_dict[order_id].meal_finished_time = time + \
                    self.order_dict[order_id].cooking_duration
                self.unassigned_order_list = [
                    o for o in self.unassigned_order_list if o.id != order_id]
                
                self.assigned_rider_to_order(order_id,rider_id)

                self.assigned_order_list.append(self.order_dict[order_id])

            elif status == OrderEnum.PICKED_UP:
                self.order_dict[order_id].picked_up_time = time

            elif status == OrderEnum.DELIVERED:
                self.assigned_order_list = [
                    o for o in self.assigned_order_list if o.id != order_id]
                self.order_dict[order_id].finished_time = time
                self.finished_order_list.append(self.order_dict[order_id])

        except:
            logger.warning(f"Order with Id {order_id} is not found.")

    def get_order_by_id(self, order_id):
        try:
            return self.order_dict[order_id]
        except:
            logger.warning(f"Order with Id {order_id} is not found.")

    def assigned_rider_to_order(self, order_id, rider_id):
        try:
            self.order_dict[order_id].rider_id = rider_id
        except:
            logger.warning(f"Order with Id {order_id} is not found.")

    def export_log_file(self):
        order_log = {
            'id': [],
            'restaurant_id': [],
            'restaurant_location_lat': [],
            'restaurant_location_lng': [],
            'customer_location_lat': [],
            'customer_location_lng': [],
            'created_time': [],
            'assigned_time': [],
            'meal_finished_time': [],
            'picked_up_time': [],
            'finished_time': [],
            'rider_id': [],
        }

        for order in self.order_dict.values():
            order_log['id'].append(order.id)
            order_log['restaurant_id'].append(order.restaurant)
            order_log['restaurant_location_lat'].append(order.restaurant_destination.location.y)
            order_log['restaurant_location_lng'].append(order.restaurant_destination.location.x)
            order_log['customer_location_lat'].append(order.customer_destination.location.y)
            order_log['customer_location_lng'].append(order.customer_destination.location.x)
            order_log['created_time'].append(order.created_time)
            order_log['assigned_time'].append(order.assigned_time)
            order_log['meal_finished_time'].append(order.meal_finished_time)
            order_log['picked_up_time'].append(order.picked_up_time)
            order_log['finished_time'].append(order.finished_time)
            order_log['rider_id'].append(order.rider_id)

        order_log_df = pd.DataFrame(data=order_log)
        order_log_df.to_csv("{}/{}".format(Config.LOG_DIR, Config.ORDER_LOG_FILENAME), index=False)
        logger.info('Exported order log file')


class Destination:
    def __init__(self, order: Order, location: Point, type: LocationEnum, ready_time: int, preparing_duration: int):
        self.location: Point = location
        self.type: LocationEnum = type
        self.ready_time: int = ready_time
        self.preparing_duration: int = preparing_duration
        self.order: Order = order

    def action(self, time):
        if self.type == LocationEnum.RESTAURANT:
            self.order.status = OrderEnum.PICKED_UP
            order_simulator.change_order_status(
                self.order.id, OrderEnum.PICKED_UP, time)
        elif self.type == LocationEnum.CUSTOMER:
            self.order.status = OrderEnum.DELIVERED
            order_simulator.change_order_status(
                self.order.id, OrderEnum.DELIVERED, time)


order_simulator = OrderSimulator()
restaurant_simulator = RestaurantSimulator()

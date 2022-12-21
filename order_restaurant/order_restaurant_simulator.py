import sys
import os
sys.path.append(os.path.abspath("..\\simulator"))
# from type_enum.order_status import OrderStatusEnum
import numpy as np
import pandas as pd
import random
from common.location import generateBangkokLocation, Coordinates
from common.order import OrderEnum
import scipy.stats
from common.location import Coordinates, LocationEnum, generateBangkokLocation

class Restaurant:

    def __init__(self,location,restaurant_idx,mean=1000,std=300):
        self.id : int = restaurant_idx
        self.location : Coordinates = location
        # queue of orderId
        self.order_id_queue : list[int]= []
        self.mean : int =mean
        self.std : int =std
 
    def rider_pickup_order(self,pickup_order):
        # check if pickup_order ready if yes
        # Pop pickup_order from order_queue
        # 
        order_simulator.change_status(pickup_order.id,OrderEnum.DELIVERING)
        self.order_id_queue=[o_id for o_id in self.order_id_queue if o_id!=pickup_order.id]

    def preparing_current_order(self,time):
        if len(self.order_id_queue) > 0:
            current_order = order_simulator.get_order_by_id(self.order_id_queue[0])
            if time>=current_order.cooking_duration and current_order.status==OrderEnum.ASSIGNED:
                #change status of order by order id
                order_simulator.change_order_status(self.order_id_queue[0],OrderEnum.READY)

    def estimate_order_cooking_duration(self,order):
        # Estimate Time from Gaussian
        # preparing time distribution.estimate sth like that

        if self.std==0:
            self.std=100

        lower_bound = 200
        upper_bound = 2500

        cooking_duration = int(scipy.stats.truncnorm.rvs((lower_bound-self.mean)/self.std,
                                            (upper_bound-self.mean)/self.std,
                                            loc=self.mean,scale=self.std,size=1)[0])
        # cooking_duration = int(np.random.normal(self.mean,self.std))
        if cooking_duration<=0:
            cooking_duration = 1000
        return cooking_duration

        # return 10

class RestaurantSimulator :
    def __init__(self):
        self.restaurant_idx : int =0
        self.restaurant_list : list[Restaurant] = []
        self.restaurant_id_list : list[int]= []
        # res_list = pd.read_csv("order_restaurant/restaurant_sample.csv")
        res_list = pd.read_csv("order_restaurant/restaurant_sample_10000.csv")
        for idx,res in res_list.iterrows():
            new_res=Restaurant(Coordinates(res["Merchant.Lat"],res["Merchant.Lng"]),self.restaurant_idx,res["mean_preparing_time"],res["std_preparing_time"])
            self.restaurant_idx+=1
            self.restaurant_list.append(new_res)
            self.restaurant_id_list.append(idx)

    def simulate(self,time):

        # loop check each restaurant
        for res_id in range(len(self.restaurant_list)):
            res=self.restaurant_list[res_id]
                
            # complete current order
            res.preparing_current_order(time)
            

    def estimate_real_cooking_duration(self,restaurant_id,order):

        res_id = self.restaurant_id_list.index(restaurant_id)

        return self.restaurant_list[res_id].estimate_order_cooking_duration(order)

    def assign_order_to_restaurant(self,restaurant_id,order):

        res_id = self.restaurant_id_list.index(restaurant_id)

        self.restaurant_list[res_id].order_id_queue.append(order.id)

    def get_restaurant_by_id(self,res_id):
        try :
            idx=self.restaurant_id_list.index(res_id)
            return self.restaurant_list[idx] 
        except:
            print("Restaurant with Id",res_id,"is not found.")
            return None

    def get_all_restaurant_id(self):
        return self.restaurant_id_list

class Order:

    def __init__(self,restaurant_id,order_idx,created_time):
        self.id : int = order_idx
        self.restaurant : int = restaurant_id
        self.restaurant_destination : Destination = None
        self.customer_destination : Destination = None
        self.created_time : int = created_time
        self.assigned_time : int = None
        self.meal_finished_time : int = None
        self.picked_up_time : int = None
        self.cooking_duration : int = None
        self.finished_time : int = 0
        self.status : OrderEnum = OrderEnum.CREATED
        self.rider =None

        
class OrderSimulator:

    def __init__(self):
        self.order_idx=0
        self.order_dict= {}
        self.finished_order_list = []
        self.unassigned_order_list = []
        self.assigned_order_list = []
        self.cancelled_order_list = []

    def simulate(self,time):
        # num order should be randomed from some distribution
        cancelled_id = []
        for order in self.unassigned_order_list:
            if time - order.created_time> 600:
                self.cancelled_order_list.append(order)
                cancelled_id.append(order.id)
        
        self.unassigned_order_list = [o for o in self.unassigned_order_list if o.id not in cancelled_id]

        restaurant_id=random.choice(restaurant_simulator.get_all_restaurant_id())
        customer_destination = generateBangkokLocation()
        self.create_order(customer_destination,restaurant_id,time)

    def create_order(self,customer_destination,restaurant_id,created_time):
        
        restaurant = restaurant_simulator.get_restaurant_by_id(restaurant_id)
        new_order=Order(restaurant_id, self.order_idx, created_time)
        new_order.cooking_duration= restaurant_simulator.estimate_real_cooking_duration(restaurant_id,new_order)
        
        new_order.restaurant_destination = Destination(new_order, restaurant.location, LocationEnum.RESTAURANT, new_order.cooking_duration)
        new_order.customer_destination = Destination(new_order, customer_destination, LocationEnum.CUSTOMER, 5)

        self.order_dict[self.order_idx]=new_order

        self.unassigned_order_list.append(new_order)

        restaurant_simulator.assign_order_to_restaurant(restaurant_id,new_order)
        
        self.order_idx+=1

    def estimate_cooking_duration(self,restaurant_id,order):

        # estimate by ML
        return 800
    
    def change_order_status(self,order_id,status,time=0):
        
        try :
            self.order_dict[order_id].status=status
            

            if status==OrderEnum.ASSIGNED:
                self.order_dict[order_id].assigned_time = time
                self.order_dict[order_id].meal_finished_time = time + self.order_dict[order_id].cooking_duration
                self.unassigned_order_list = [o for o in self.unassigned_order_list if o.id!=order_id]
                self.assigned_order_list.append(self.order_dict[order_id])

            elif status==OrderEnum.PICKED_UP:
                self.order_dict[order_id].picked_up_time = time

            elif status==OrderEnum.DELIVERED:
                self.assigned_order_list = [o for o in self.assigned_order_list if o.id!=order_id]
                self.order_dict[order_id].finished_time = time
                self.finished_order_list.append(self.order_dict[order_id])

        except:
            print("Order with Id",order_id,"is not found.")
    
    def get_order_by_id(self,order_id):
        try :
            return self.order_dict[order_id]
        except:
            print("Order with Id",order_id,"is not found.")

    def assigned_rider_to_order(self,order_id,rider_id):
        try :
            self.order_dict[order_id].rider=rider_id
        except:
            print("Order with Id",order_id,"is not found.")

class Destination :
    def __init__(self, order : Order, location : Coordinates, type : LocationEnum, ready_time : int):
        self.location : Coordinates = location
        self.type : LocationEnum = type
        self.ready_time : int = ready_time
        self.order : Order = order
    
    def pick_up_or_deliver(self, time):
        if self.type == LocationEnum.RESTAURANT:
            self.order.status = OrderEnum.PICKED_UP
            order_simulator.change_order_status(self.order.id,OrderEnum.PICKED_UP, time)
        elif self.type == LocationEnum.CUSTOMER:
            self.order.status = OrderEnum.DELIVERED
            order_simulator.change_order_status(self.order.id,OrderEnum.DELIVERED, time)
order_simulator = OrderSimulator()
restaurant_simulator = RestaurantSimulator()
import sys
import os
sys.path.append(os.path.abspath("..\\simulator"))
# from type_enum.order_status import OrderStatusEnum
import numpy as np
import pandas as pd
import random
from common.location import generateBangkokLocation_2 ,Coordinates
from common.order import OrderEnum

class Restaurant:

    def __init__(self,location,restaurant_idx,mean=800,std=100):
        self.id = restaurant_idx
        self.location = location
        # queue of orderId
        self.order_id_queue = []
        self.mean=mean
        self.std=std
 
    def rider_pickup_order(self,pickup_order):
        # check if pickup_order ready if yes
        # Pop pickup_order from order_queue
        # 
        order_simulator.change_status(pickup_order.id,OrderEnum.DELIVERING)
        self.order_id_queue=[o_id for o_id in self.order_id_queue if o_id!=pickup_order.id]

    def preparing_current_order(self,time):
        if len(self.order_id_queue) > 0:
            current_order = order_simulator.get_order_by_id(self.order_id_queue[0])
            if time>=current_order.ready_time and current_order.status==OrderEnum.READY:
                #change status of order by order id
                order_simulator.change_order_status(self.order_id_queue[0],OrderEnum.READY)

    def estimate_order_ready_time(self,order):
        # Estimate Time from Gaussian
        # preparing time distribution.estimate sth like that
        return int(np.random.normal(self.mean,self.std))

        # return 10

class RestaurantSimulator :
    def __init__(self):
        self.restaurant_idx=0
        self.restaurant_list = []
        self.restaurant_id_list = []
        res_list = pd.read_csv("order_restaurant/restaurant_sample.csv")
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
            

    def estimate_real_ready_time(self,restaurant_id,order):

        res_id = self.restaurant_id_list.index(restaurant_id)

        return self.restaurant_list[res_id].estimate_order_ready_time(order)

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

    def __init__(self, destination,restaurant_id,restaurant_location,order_idx,created_time):
        self.id = order_idx
        self.restaurant = restaurant_id
        self.restaurant_location = restaurant_location
        self.destination = destination
        self.created_time = created_time
        self.ready_time = None
        self.status = OrderEnum.CREATED
        self.rider=None

        
class OrderSimulator:

    def __init__(self):
        self.order_idx=0
        self.order_dict= {}
        self.finished_order_list = []
        self.unassigned_order_list = []
        self.assigned_order_list = []

    def simulate(self,time):
        # num order should be randomed from some distribution
        restaurant_id=random.choice(restaurant_simulator.get_all_restaurant_id())
        destination = generateBangkokLocation_2()
        self.create_order(destination,restaurant_id,time)

    def create_order(self,destination,restaurant_id,created_time):
        
        restaurant = restaurant_simulator.get_restaurant_by_id(restaurant_id)

        new_order=Order(destination, restaurant_id, restaurant.location, self.order_idx, created_time)
        
        new_order.ready_time= restaurant_simulator.estimate_real_ready_time(restaurant_id,new_order)
        
        self.order_dict[self.order_idx]=new_order

        self.unassigned_order_list.append(new_order)

        restaurant_simulator.assign_order_to_restaurant(restaurant_id,new_order)
        
        self.order_idx+=1

    def estimate_ready_time(self,restaurant_id,order):

        # estimate by ML
        return 10
    
    def change_order_status(self,order_id,status):
        
        try :
            self.order_dict[order_id].status=status

            if status==OrderEnum.ASSIGNED:
                self.unassigned_order_list = [o for o in self.unassigned_order_list if o.id!=order_id]
                self.assigned_order_list.append(self.order_dict[order_id])

            if status==OrderEnum.DELIVERED:
                self.assigned_order_list = [o for o in self.assigned_order_list if o.id!=order_id]
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


order_simulator = OrderSimulator()
restaurant_simulator = RestaurantSimulator()
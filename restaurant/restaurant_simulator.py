import sys
import os
sys.path.append(os.path.abspath("..\\simulator"))

from order.order_simulator import  OrderSimulator
from type_enum.order_status import OrderStatusEnum
import numpy as np
class Restaurant:

    def __init__(self,location,restaurant_idx,mean=800,std=100):
        self.id = restaurant_idx
        self.location = location
        # queue of orderId
        self.order_id_queue = []
        self.preparing_time_mean=mean
        self.preparing_time_std=std
 
    def rider_pickup_order(self,pickup_order):
        # check if pickup_order ready if yes
        # Pop pickup_order from order_queue
        # 
        OrderSimulator.change_status(pickup_order.id,OrderStatusEnum.DELIVERING)
        self.order_id_queue=[o_id for o_id in self.order_id_queue if o_id!=pickup_order.id]

    def preparing_current_order(self,time):

        current_order = OrderSimulator.get_order_by_id(self.order_id_queue[0])
        if time>=current_order.readyTime and current_order.status==OrderStatusEnum.COOKED:
            #change status of order by order id
            OrderSimulator.change_order_status(self.order_id_queue[0],OrderStatusEnum.COOKED)

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

        order.readyTime = self.estimate_real_ready_time(restaurant_id,order)
        self.restaurant_list[res_id].order_queue(order)

    def get_restaurant_by_id(self,res_id):
        try :
            idx=self.restaurant_id_list.index(res_id)
            return self.restaurant_list[idx] 
        except:
            print("Restaurant with Id",res_id,"is not found.")
            return None

    def get_all_restaurant_id(self):
        return self.restaurant_id_list

    
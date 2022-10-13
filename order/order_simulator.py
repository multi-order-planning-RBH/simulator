import random
from restaurant.restaurant_simulator import RestaurantSimulator
from type_enum.location import generateBangkokLocation
from type_enum.order_status import OrderStatusEnum

class Order:

    def __init__(self, destination,restaurant_id,order_idx,created_time):
        self.id = order_idx
        self.restaurant = restaurant_id
        self.destination = destination
        self.created_time = created_time
        self.ready_time = None
        self.status = OrderStatusEnum.CREATED
        self.rider=None

        #Complete order 
        #self.finish_time 

        
class OrderSimulator:

    def __init__(self):
        self.order_idx=0
        self.order_dict= {}
        self.finished_order_list = []
        self.unassigned_order_list = []
        self.assigned_order_list = []

    def simulate(self,time):
        # num order should be randomed from some distribution
        restaurant_id=random.choice(RestaurantSimulator.get_all_restaurant_id())
        destination = generateBangkokLocation()
        self.create_order(destination,restaurant_id,time)

    def create_order(self,destination,restaurant_id,created_time):

        new_order=Order(destination, restaurant_id, self.order_idx, created_time)
        
        new_order.ready_time= RestaurantSimulator.estimate_real_ready_time(restaurant_id,new_order)
        
        self.order_list[self.order_idx]=new_order

        self.unassigned_order_list.append(new_order)
        self.order_id_list.append(new_order.id)

        RestaurantSimulator.assign_order_to_restaurant(restaurant_id,new_order)
        
        self.order_idx+=1

    def estimate_ready_time(self,restaurant_id,order):

        # estimate by ML
        return 10
    
    def change_order_status(self,order_id,status):
        
        try :
            self.order_dict[order_id].status=status

            if status==OrderStatusEnum.ASSIGNED:
                self.unassigned_order_list = [o for o in self.unassigned_order_list if o.id!=order_id]
                self.assigned_order_list.append(self.order_dict[order_id])

            if status==OrderStatusEnum.DELIVERED:
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



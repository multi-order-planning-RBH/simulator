import random

from restaurant_simulator import RestaurantSimulator


class Order:

    def __init__(self, destination,restaurant_id,order_idx,created_time,ready_time):
        self.id = order_idx
        self.restaurant = restaurant_id
        self.destination = destination
        self.created_time = created_time
        self.ready_time = ready_time
        self.status = "Created"
        self.rider=None

        #Complete order 
        #self.finish_time 

        
class OrderSimulator:

    def __init__(self):
        self.order_idx=0
        self.order_list = []
        #self.assigned_order_list 
        #self.unassigned_order_list 
        #self.finish_list 

        self.order_id_list = []

    def simulate(self,time):
        # num order should be randomed from some distribution
        num_order = random.randint(0,100)
        for i in range(num_order):
            restaurant_id=random.choice(RestaurantSimulator.get_all_restaurant_id())
            destination = generateBangkokLocation()
            self.create_order(destination,restaurant_id,time)

    def create_order(self,destination,restaurant_id,created_time):

        restuarant = RestaurantSimulator.get_restaurant_by_id(restaurant_id)
        estimated_real_ready_time=restuarant.estimate_order_ready_time()

        new_order=Order(destination, restaurant_id, self.order_idx, created_time, estimated_real_ready_time)
        
        self.order_list.append(new_order)
        self.order_id_list.append(new_order.id)

        self.order_idx+=1

    def estimate_ready_time(self,restaurant_id,order):

        # estimate by ML
        return 10
    
    def change_order_status(self,order_id,status):
        
        try :
            idx=self.order_id_list.index(order_id)
            self.order_list[idx].status=status
        except:
            print("Order with Id",order_id,"is not found.")
    
    def get_order_by_id(self,order_id):
        try :
            idx=self.order_id_list.index(order_id)
            return self.order_list[idx] 
        except:
            print("Order with Id",order_id,"is not found.")
            return None




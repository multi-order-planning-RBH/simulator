from order_simulator import Order, OrderSimulator

class Restaurant:

    def __init__(self,location,restaurant_idx):
        self.id = restaurant_idx
        self.location = location
        # queue of orderId
        self.order_id_queue = []
        self.preparing_time_distribution=None
 
    def rider_pickup_order(self,pickup_order):
        # check if pickup_order ready if yes
        # Pop pickup_order from order_queue
        # 
        OrderSimulator.change_status(pickup_order.id,"Picked Up")
        self.order_id_queue=[o_id for o_id in self.order_id_queue if o_id!=pickup_order.id]

    def check_rider_arrive(self,rider):

        # if rider is not too far from 
        return True

    def preparing_current_order(self,time):

        current_order = OrderSimulator.get_order_by_id(self.order_id_queue[0])
        if time>=current_order.readyTime and current_order.status=="NotReady":
            #change status of order by order id
            OrderSimulator.change_order_status(self.order_id_queue[0],"Ready")

    def estimate_order_ready_time(self,order):
        # Estimate Time from Gaussian
        # preparing time distribution.estimate sth like that
        return 10

class RestaurantSimulator :
    def __init__(self):
        self.restaurant_idx=0
        self.restaurant_list = []
        self.restaurant_id_list = []

    def simulate(self,time):

        # loop check each order if its done and rider arrive
        for res_id in range(len(self.restaurant_list)):
            for ord_id in self.restaurant_list[res_id].order_id_queue:
                
                
                res=self.restaurant_list[res_id]
                order=OrderSimulator.get_order_by_id(ord_id)

                rider = RiderSimulator.get_rider(order.rider)
                

                # check if rider arrive
                # if rider arrive and if order ready , rider_pickup_order
                if order.status=="Ready" and res.check_rider_arrive(rider):
                    res.rider_pickup_order(order)
            # complete current order
            res.preparing_current_order(time)
        
        # receive new order from order simulator

    def estimate_real_ready_time(self,restaurant_id,order_id):

        res_id = self.restaurant_id_list.index(restaurant_id)

        return self.restaurant_list[res_id].estimate_current_order_ready_time(order_id)

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

    
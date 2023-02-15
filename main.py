import time
import os
import time
import pandas as pd
import random
import numpy as np


from manager.central_manager import CentralManager
from rider.rider_simulator import rider_simulator
from order_restaurant.order_restaurant_simulator import order_simulator, restaurant_simulator
from suggester.multi_order_suggester import MultiOrderSuggester
from common.system_logger import SystemLogger
from map.map import sample_points_on_graph
from config import Config

logger = SystemLogger(__name__)

random.seed(Config.SEED)
np.random.seed(Config.SEED)

def main():
    start = time.time()

    order = order_simulator
    restaurant = restaurant_simulator
    
    rider = rider_simulator
    multi_order = MultiOrderSuggester(rider_simulator=rider, order_simulator=order)

    manager = CentralManager(rider_simulator=rider, restaurant_simulator=restaurant, \
        order_simulator=order, multi_order_suggester=multi_order,log_step=Config.ORDER_LOGGING_PERIOD)
    manager.simulate(Config.CENTRAL_MANAGER_SIMULATION_TIME, Config.CENTRAL_MANAGER_TIME_WINDOW)

    logger.info(f"Customer Waiting Time:           {manager.calculate_customer_waiting_time()}")
    logger.info(f"Rider onroad time:               {manager.calculate_rider_utilization_time()}")
    logger.info(f"Number of order per rider:                 {manager.calculate_rider_order_count()}")
    logger.info(f"Count no order rider:                 {manager.count_no_order_rider()}")
    logger.info(f"Number of cancelled order:                 {len(order.cancelled_order_list)}")
    logger.info(f"Computation time:                {time.time()-start}")
    logger.info(f"Number of assigning:             {rider_simulator.count}")
    logger.info(f"Number of success assigning:     {rider_simulator.success_count}")
    print("Customer Waiting Time:           ", manager.calculate_customer_waiting_time())
    print("Number of finished order:           ", len(order.finished_order_list))
    print("Number of cancelled order:                 ", len(order.cancelled_order_list))
    print("Number of unassigned orders :    ", len(order.unassigned_order_list))
    print("Number of assigned orders :      ", len(order.assigned_order_list))
    print("Rider onroad time:               ", manager.calculate_rider_utilization_time())
    print("Number of order per rider:                 ", manager.calculate_rider_order_count())
    print("Count no order rider:                 ", manager.count_no_order_rider())
    print("Computation time:                ", time.time()-start)
    print("Number of assigning:             ", rider_simulator.count)
    print("Number of success assigning:     ", rider_simulator.success_count)
    
    

    dir_name = "log/"

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    order_summary_log_df = pd.DataFrame(manager.order_log)
    order_summary_log_df.to_csv(dir_name+"order_summary_log.csv",index=False)

    order_log_df = pd.DataFrame(columns = ["id","restaurant_destination","customer_destination","created_time"
                        ,"assigned_time","meal_finished_time","picked_up_time","cooking_duration"
                        ,"estimated_cooking_duration","finished_time","status","rider_id"])
    
    all_order_list = []
    all_order_list+=order.finished_order_list
    all_order_list+=order.cancelled_order_list
    all_order_list+=order.assigned_order_list
    all_order_list+=order.unassigned_order_list

    o_list = []
    for o in all_order_list:
        attr_list = []

        for col in order_log_df.columns:
            attr=getattr(o,col)
            if col in ["restaurant_destination","customer_destination"]:
                attr = attr.location
            if col=="rider" and attr:
                attr = attr.id
            attr_list.append(attr)

        o_list.append(attr_list)
    order_log_df = pd.concat([order_log_df,pd.DataFrame(o_list,columns=order_log_df.columns)])
    order_log_df.to_csv(dir_name+"order_log.csv",index=False)

if __name__ == "__main__":
    main()

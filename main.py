import time
import os
import time
import pandas as pd
import numpy as np
import random

from common.system_logger import SystemLogger

from manager.central_manager import CentralManager
from rider.rider_simulator import rider_simulator
from order_restaurant.order_restaurant_simulator import order_simulator, restaurant_simulator
from suggester.multi_order_suggester import MultiOrderSuggester
from config import Config, config_dict

logger = SystemLogger(__name__)
os.environ["PYTHONHASHSEED"] = str(Config.SEED)
random.seed(Config.SEED)
np.random.seed(Config.SEED)

def main():
    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)
    logger.info("LOG_DIR: {}".format(Config.LOG_DIR))
    start = time.time()

    order = order_simulator
    restaurant = restaurant_simulator
    rider = rider_simulator

    multi_order = MultiOrderSuggester(rider_simulator=rider, order_simulator=order)
    manager = CentralManager(rider_simulator=rider, restaurant_simulator=restaurant, \
        order_simulator=order, multi_order_suggester=multi_order,log_step=Config.ORDER_LOG_PERIOD)
    manager.simulate(Config.CENTRAL_MANAGER_SIMULATION_TIME, Config.CENTRAL_MANAGER_TIME_WINDOW)
    
    get_key_metrics(manager, order, rider, start)

    order_summary_log_df = pd.DataFrame(manager.order_log)
    order_summary_log_df.to_csv(Config.LOG_DIR+"/order_summary_log.csv",index=False)

    log_seed_arr = pd.DataFrame({"batch_result":manager.multi_order_suggester.log_batch_result})
    log_seed_arr.to_csv(Config.LOG_DIR+"/log_batch.csv",index=False)

def get_key_metrics(manager, order, rider_simulator, start):
    key_metrics = {}
    key_metrics["CUSTOMER_WAITING_TIME"] = manager.calculate_customer_waiting_time()
    key_metrics["RIDER_ONROAD_TIME"] = manager.calculate_rider_utilization_time()
    key_metrics["NUMBER_OF_ORDER_PER_RIDER"] = manager.calculate_rider_order_count()
    key_metrics["COUNT_NO_ORDER_RIDER"] = manager.count_no_order_rider()
    key_metrics["NUMBER_OF_CANCELLED_ORDER"] = len(order.cancelled_order_list)
    key_metrics["NUMBER_OF_FINISHED_ORDER"] = len(order.finished_order_list)
    key_metrics["NUMBER_OF_UNASSIGNED_ORDER"] = len(order.unassigned_order_list)
    key_metrics["NUMBER_OF_ASSIGNED_ORDER"] = len(order.assigned_order_list)
    key_metrics["COMPUTATION_TIME"] = time.time()-start
    key_metrics["NUMBER_OF_ASSIGNING"] = rider_simulator.count
    key_metrics["NUMBER_OF_SUCCESS_ASSIGNING"] = rider_simulator.success_count

    data = {'key': key_metrics.keys(), 'value': key_metrics.values()}
    value = list(key_metrics.values())
    key_metrics_df = pd.DataFrame(data=data).T
    key_metrics_df.to_csv(Config.LOG_DIR+"/key_metrics.csv",index=False)

    data = {'key': config_dict.keys(), 'value': config_dict.values()}
    config_df = pd.DataFrame(data=data)
    config_df.to_csv(Config.LOG_DIR+"/config.csv",index=False)

    logger.info(f"Customer Waiting Time:           {value[0]}")
    logger.info(f"Rider onroad time:               {value[1]}")
    logger.info(f"Number of order per rider:                 {value[2]}")
    logger.info(f"Count no order rider:                 {value[3]}")
    logger.info(f"Number of cancelled order:                 {value[4]}")
    logger.info(f"Number of finished order:                 {value[5]}")
    logger.info(f"Number of unassigned order:                 {value[6]}")
    logger.info(f"Number of assigned order:                 {value[7]}")
    logger.info(f"Computation time:                {value[8]}")
    logger.info(f"Number of assigning:             {value[9]}")
    logger.info(f"Number of success assigning:     {value[10]}")

    

if __name__ == "__main__":
    main()

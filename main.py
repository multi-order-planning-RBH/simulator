import time
import os
import time
import pandas as pd

from manager.central_manager import CentralManager
from rider.rider_simulator import rider_simulator
from order_restaurant.order_restaurant_simulator import order_simulator, restaurant_simulator
from suggester.multi_order_suggester import MultiOrderSuggester
from common.system_logger import SystemLogger
from config import Config

logger = SystemLogger(__name__)

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

    dir_name = "log"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    order_log_df = pd.DataFrame(manager.order_log)
    order_log_df.to_csv("log/order_log.csv",index=False)

if __name__ == "__main__":
    main()

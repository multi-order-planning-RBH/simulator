from map.map import number_of_fail_findding_path
from manager.mode import CentralManagerMode
from config import Config
from common.system_logger import SystemLogger
import numpy as np

logger = SystemLogger(__name__)

class CentralManager:
    def __init__(self, rider_simulator, restaurant_simulator, order_simulator, multi_order_suggester,log_step=1000):
        self.current_time = 0
        self.failed_mode = 0
        self.rider_simulator = rider_simulator
        self.restaurant_simulator = restaurant_simulator
        self.order_simulator = order_simulator
        self.multi_order_suggester = multi_order_suggester
        self.mode = Config.MODE
        self.log_step = log_step
        self.order_log = {"timesteps":[],"customer_waiting_time":[],
                        "rider_onroad_time":[],"rider_order_count":[],
                        "#cancelled_order":[],"#unassigned_order":[],
                        "#assigned_order":[],"#finished_order":[]}
        
    def calculate_customer_waiting_time(self):
        sum_waiting_time = 0
        finished_order_list = self.order_simulator.finished_order_list

        for order in finished_order_list:
            sum_waiting_time += order.finished_time - order.created_time

        if len(finished_order_list)>0:
            return sum_waiting_time / len(self.order_simulator.finished_order_list)
        else:
            return -1
            

    def calculate_rider_utilization_time(self):
        sum_utilization_time = 0
        riders = self.rider_simulator.riders
        for rider in riders:
            sum_utilization_time += rider.utilization_time
        if len(riders)>0:
            return sum_utilization_time / len(riders)
        else:
            return -1

    def calculate_rider_order_count(self):
        sum_order_count = 0
        riders = self.rider_simulator.riders
        for rider in riders:
            sum_order_count += rider.cum_order_count
        if len(riders)>0:
            return sum_order_count / len(riders)
        else:
            return -1

    def count_no_order_rider(self):
        no_order_count = 0
        riders = self.rider_simulator.riders
        for rider in riders:
            if rider.order_count==0:
                no_order_count += rider.order_count
        if len(riders)>0:
            return no_order_count
        else:
            return -1

    def simulate(self, total_time: int, time_window: int):
        while self.current_time < total_time:
            time = self.current_time
            self.order_simulator.simulate(time)
            self.restaurant_simulator.simulate(time)
            self.rider_simulator.simulate(time)

            rider_list = self.rider_simulator.unassigned_riders
            working_rider_list = self.rider_simulator.working_riders
            order_list = self.order_simulator.unassigned_order_list
            assigned_order_list = self.order_simulator.assigned_order_list
            finished_order_list = self.order_simulator.finished_order_list

            if time % self.log_step == 0:
                # print("Time : ", time)
                # print("Number of available riders :     ", len(rider_list))
                # print("Number of working riders :       ", len(working_rider_list))
                # print("Number of unassigned orders :    ", len(order_list))
                # print("Number of assigned orders :      ", len(assigned_order_list))
                # print("Number of finished orders :      ", len(finished_order_list))
                # print()
                logger.info(f"Time : {time}")
                logger.info(f"Number of available riders :     {len(rider_list)}")
                logger.info(f"Number of working riders :       {len(working_rider_list)}")
                logger.info(f"Number of unassigned orders :    {len(order_list)}")
                logger.info(f"Number of assigned orders :      {len(assigned_order_list)}")
                logger.info(f"Number of finished orders :      {len(finished_order_list)}")
                logger.info(f"Number of fail findding path:    {number_of_fail_findding_path[0]}")

                self.order_log["timesteps"].append(time)
                self.order_log["customer_waiting_time"].append(self.calculate_customer_waiting_time())
                self.order_log["rider_onroad_time"].append(self.calculate_rider_utilization_time())
                self.order_log["rider_order_count"].append(self.calculate_rider_order_count())
                self.order_log["#finished_order"].append(len(finished_order_list))
                self.order_log["#cancelled_order"].append(len(self.order_simulator.cancelled_order_list))
                self.order_log["#unassigned_order"].append(len(order_list))
                self.order_log["#assigned_order"].append(len(assigned_order_list))

                # print("Time :", time)
                # print("Number of available riders :     ", len(rider_list))
                # print("Number of working riders :       ", len(working_rider_list))
                # print("Number of unassigned orders :    ", len(order_list))
                # print("Number of assigned orders :      ", len(assigned_order_list))
                # print("Number of cancel orders :      ", self.order_log["#cancelled_order"][-1])
                # print("Number of finished orders :      ", len(finished_order_list))
                # if self.mode == CentralManagerMode.BATCH:  
                #     print("Number of failed assignment  ", self.failed_mode)
                # print()

            if self.mode == CentralManagerMode.BATCH:
                if self.current_time > 0 and self.current_time % time_window == 0:
                    try:
                        self.multi_order_suggester.suggest_batch_mode(time)
                    except Exception as e: 
                        print(e)
                        self.failed_mode += 1
                        self.multi_order_suggester.assign_order_to_rider(time)
            elif self.mode == CentralManagerMode.ONLINE:
                self.multi_order_suggester.suggest_online_mode(time)
            else:
                if self.current_time > 0 and self.current_time % time_window == 0:
                    self.multi_order_suggester.assign_order_to_rider(time)

            self.current_time += 1

        self.order_simulator.export_log_file()

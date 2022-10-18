class CentralManager:
    def __init__(self, rider_simulator, restaurant_simulator, order_simulator, multi_order_suggester):
        self.current_time = 0
        self.rider_simulator = rider_simulator
        self.restaurant_simulator = restaurant_simulator
        self.order_simulator = order_simulator
        self.multi_order_suggester = multi_order_suggester
        
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
            sum_order_count += rider.order_count
        if len(riders)>0:
            return sum_order_count / len(riders)
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

            if time % 1000 == 0:
                print("Time : ", time)
                print("Number of available riders :     ", len(rider_list))
                print("Number of working riders :       ", len(working_rider_list))
                print("Number of unassigned orders :    ", len(order_list))
                print("Number of assigned orders :      ", len(assigned_order_list))
                print("Number of finished orders :      ", len(finished_order_list))
                print()

            if self.current_time > 0 and self.current_time % time_window == 0:
                self.multi_order_suggester.assign_order_to_rider(time)

            self.current_time += 1

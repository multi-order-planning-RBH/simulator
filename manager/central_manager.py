class CentralManager:
    def __init__(self):
        self.current_time = 0
        self.rider_simulator = None
        self.restaurant_simulator = None
        self.order_simulator = None
        self.multi_order_suggester = None

    def tick_clock(self):
        self.current_time += 1

    def calculate_customer_waiting_time(self):
        pass

    def calculate_rider_availability(self):
        pass

    def simulate(self, total_time: int, time_window: int):
        while self.current_time < total_time:
            self.order_simulator.simulate()
            self.restaurant_simulator.simulate()
            self.rider_simulator.simulate()

            if self.current_time > 0 and self.current_time % time_window == 0:
                self.multi_order_suggester.assign_order_to_rider()

            self.tick_clock()

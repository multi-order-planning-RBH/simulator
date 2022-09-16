class CentralManager:
    def __init__(self):
        self.current_time = 0
        self.rider_simulator = None
        self.restaurant_simulator = None
        self.order_simulator = None

    def tick_clock(self):
        self.current_time += 1

    def calculate_customer_waiting_time(self):
        pass

    def calculate_rider_availability(self):
        pass

    def simulate(self):
        pass
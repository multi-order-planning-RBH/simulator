import sys, os
sys.path.append(os.path.abspath("./"))
from common.location import generateBangkokLocation_2
from rider.rider_simulator import RiderSimulator
from rider.rider import Order
import time
import random

number_of_rider = 10000

if __name__ == '__main__':
    riderSimulator = RiderSimulator()
    time1 = time.time()
    
    for _ in range(number_of_rider):
        riderSimulator.create_rider_innitial_location()

    order_id = 0

    for t in range(1440):
        restaurant_location = generateBangkokLocation_2()
        destination_location = generateBangkokLocation_2()
        created_time = t
        ready_time = t+30
        order_id += 1
        order = Order(destination_location, restaurant_location, 1, created_time, ready_time)

        rider_index = random.randrange(0, number_of_rider)
        riderSimulator.assign_order_to_a_rider(order, riderSimulator.riders[rider_index], t)
        riderSimulator.simulate(t)
    
    print(time.time()-time1)

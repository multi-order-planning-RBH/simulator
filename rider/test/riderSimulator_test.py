from multiprocessing import freeze_support
from riderSimulator import RiderSimulator
from rider import TempOrder
import time

resraurantLocation = [13.744740, 100.531876]
destination = [13.741291, 100.528645]
orderTime = 0
readyTime = 30
order = TempOrder(resraurantLocation, destination, orderTime, readyTime)

if __name__ == '__main__':
    riderSimulator = RiderSimulator()
    time1 = time.time()
    for _ in range(50000):
        riderSimulator.create_rider_innitial_location()

    riderSimulator.assign_order_to_a_rider(order=order, rider=riderSimulator.riders[0])

    riderSimulator.simulate(0)
    riderSimulator.simulate(1)
    riderSimulator.simulate(2)
    riderSimulator.simulate(3)
    print(riderSimulator.riders[0].current_action.action, riderSimulator.riders[0].current_action.action)
    print(time.time()-time1)

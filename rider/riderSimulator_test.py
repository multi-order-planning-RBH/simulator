from multiprocessing import freeze_support
from riderSimulator import RiderSimulator

if __name__ == '__main__':
    riderSimulator = RiderSimulator()
    for _ in range(10):
        riderSimulator.create_rider_innitial_location()
    riderSimulator.simulate(0)
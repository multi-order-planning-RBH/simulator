from datetime import datetime

from manager.mode import CentralManagerMode

now = datetime.now()
date_time = now.strftime("%Y%m%d_%H:%M:%S")

class Config:
    #simulation time
    CENTRAL_MANAGER_SIMULATION_TIME = 12000
    CENTRAL_MANAGER_TIME_WINDOW = 240

    #rider
    RIDER_SPEED_MEAN = 5.318089655268194
    RIDER_SPEED_STD = 1.9188270198967308
    RIDER_SPEED_LOWER_BOUND = 0.05694768987719012
    RIDER_SPEED_UPPER_BOUND = 10.847062932978952
    RIDER_LOGGING_PERIOD = 30
    RIDER_NUMBER = 100
    RIDER_STARTING_TIME = 0
    RIDER_LOG_FILENAME = "rider.csv"

    #order
    ORDER_LOGGING_PERIOD = RIDER_LOGGING_PERIOD

    #order
    ORDER_LOG_FILENAME = "order.csv"

    #map
    MAP_NORTH = 13.864249 
    MAP_EAST = 100.614548
    MAP_SOUTH = 13.806425
    MAP_WEST = 100.530755
    # MAP_NORTH = 13.914579
    # MAP_SOUTH = 13.738166 
    # MAP_EAST = 100.661622
    # MAP_WEST = 100.484028

    #central_manager
    MODE = CentralManagerMode.NORMAL
    CENTRAL_MANAGER_SIMULATION_TIME  = 10001
    CENTRAL_MANAGER_TIME_WINDOW = 100

    #random seed
    SEED = 0
    
    #log 
    LOG_DIR = "./log/{}".format(date_time)

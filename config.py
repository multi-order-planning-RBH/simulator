from datetime import datetime

from manager.mode import CentralManagerMode

now = datetime.now()
date_time = now.strftime("%Y%m%d_%H_%M_%S")

class Config:
    #simulation time
    CENTRAL_MANAGER_SIMULATION_TIME = 50400
    CENTRAL_MANAGER_TIME_WINDOW = 240
    SEED_RESET_PERIOD = 1

    #rider
    RIDER_SPEED = 5.563781044552085e-05
    RIDER_LOGGING_PERIOD = 30
    RIDER_NUMBER = 10
    RIDER_STARTING_TIME = 0
    RIDER_GETOFF_TIME = CENTRAL_MANAGER_SIMULATION_TIME

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
    MODE = CentralManagerMode.ONLINE

    #random seed
    SEED = 0
    
    #log 
    LOG_DIR = "log/{}".format(date_time)

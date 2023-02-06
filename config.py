from datetime import datetime

now = datetime.now()
date_time = now.strftime("%Y%m%d_%H:%M:%S")

class Config:
    #simulation time
    SIMULATION_TIME = 50400

    #rider
    RIDER_SPEED = 5.563781044552085e-05
    RIDER_LOGGING_PERIOD = 30
    RIDER_NUMBER = 50
    RIDER_STARTING_TIME = 0
    RIDER_GETOFF_TIME = SIMULATION_TIME

    #order
    ORDER_LOGGING_PERIOD = RIDER_LOGGING_PERIOD

    #order
    ORDER_LOG_FILENAME = "order.csv"

    #map
    MAP_NORTH = 13.914579
    MAP_SOUTH = 13.738166 
    MAP_EAST = 100.661622
    MAP_WEST = 100.484028

    #central_manager
    MODE = "online"

    #log 
    LOG_DIR = "./log/{}".format(date_time)

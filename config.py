from datetime import datetime

now = datetime.now()
date_time = now.strftime("%Y%m%d_%H:%M:%S")

class Config:
    #rider
    RIDER_SPEED = 2.0843974744180143e-05
    RIDER_LOGGING_PERIOD = 30
    RIDER_NUMBER = 100
    RIDER_STARTING_TIME = 0
    RIDER_GETOFF_TIME = 10000

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

import yaml
from datetime import datetime

from manager.mode import CentralManagerMode

with open("./config.yaml", 'r') as stream:
    config_dict = yaml.safe_load(stream)

now = datetime.now()
date_time = now.strftime("%Y%m%d_%H%M%S")

class Config:
    #rider
    RIDER_SPEED_MEAN = config_dict['rider']['speed_mean']
    RIDER_SPEED_STD = config_dict['rider']['speed_std']
    RIDER_SPEED_LOWER_BOUND = config_dict['rider']['speed_lower_bound']
    RIDER_SPEED_UPPER_BOUND = config_dict['rider']['speed_upper_bound']
    RIDER_NUMBER = config_dict['rider']['number']
    RIDER_STARTING_TIME = config_dict['rider']['starting_time']
    RIDER_GETOFF_TIME = config_dict['rider']['getoff_time']
    RIDER_LOG_PERIOD = config_dict['rider']['log_period']
    RIDER_LOCATION_LOG_FILENAME = config_dict['rider']['location_log_filename']
    RIDER_DESTINATION_LOG_FILENAME = config_dict['rider']['destination_log_filename']

    #order
    ORDER_LOG_PERIOD = config_dict['order']['log_period']

    #order
    ORDER_LOG_FILENAME = config_dict['order']['log_filename']

    #map
    MAP_NORTH = config_dict['map']['north']
    MAP_EAST = config_dict['map']['east']
    MAP_SOUTH = config_dict['map']['south']
    MAP_WEST = config_dict['map']['west']

    #central_manager
    MODE = config_dict['central_manager']['mode']
    CENTRAL_MANAGER_SIMULATION_TIME = config_dict['central_manager']['simulation_time']
    CENTRAL_MANAGER_TIME_WINDOW = config_dict['central_manager']['time_window']

    #random seed
    SEED = config_dict['seed']
    
    #log 
    LOG_DIR = "{}{}".format(config_dict['log_dir'], date_time)

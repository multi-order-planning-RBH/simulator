import pandas as pd
import random 

class ConfigAndShared:
    RELATIVE_LOGGING_PATH = "log/20230205_13:37:32/rider_location.csv"
    LOCATION_LOGGING_PATH = "./{}".format(RELATIVE_LOGGING_PATH)

    RELATIVE_LOGGING_PATH = "log/20230205_13:37:32/rider_destination.csv"
    DESTINATION_LOGGING_PATH = "./{}".format(RELATIVE_LOGGING_PATH)

    LOCAITON_DF = pd.read_csv(LOCATION_LOGGING_PATH)
    DESTINATION_DF = pd.read_csv(RELATIVE_LOGGING_PATH)

    NUMBER_OF_RIDERS = len(LOCAITON_DF['id'].unique())
    COLORS = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(NUMBER_OF_RIDERS)]

    TIME_UNIQUE = LOCAITON_DF['time'].unique()
    NUMBER_OF_TIME_STEP = len(TIME_UNIQUE)
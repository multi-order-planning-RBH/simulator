import pandas as pd
import random 

def get_restaurant_df(ORDER_DF:pd.DataFrame):
    restaurant_id = ORDER_DF['restaurant_id'].unique()
    restaurant_df = ORDER_DF.loc[restaurant_id][['restaurant_id', 'restaurant_location_lat', 'restaurant_location_lng']]
    restaurant_df = restaurant_df.rename(
        columns = {
            "restaurant_id":"id",
            "restaurant_location_lat": "lat", 
            "restaurant_location_lng": "lng"
            }
        )
    return restaurant_df

class ConfigAndShared:
    SIMULATION_DATE = "20230226_170219"

    LOCATION_LOGGING_PATH = "./log/{}/rider_location.csv".format(SIMULATION_DATE)
    DESTINATION_LOGGING_PATH = "./log/{}/rider_destination.csv".format(SIMULATION_DATE)
    ORDER_LOGGING_PATH = "./log/{}/order.csv".format(SIMULATION_DATE)

    RIDER_LOCAITON_DF = pd.read_csv(LOCATION_LOGGING_PATH)
    
    RIDER_DESTINATION_DF = pd.read_csv(DESTINATION_LOGGING_PATH)
    ORDER_DF = pd.read_csv(ORDER_LOGGING_PATH)
    RESTAURANT_DF = get_restaurant_df(ORDER_DF)

    NUMBER_OF_RIDERS = len(RIDER_LOCAITON_DF['id'].unique())
    COLORS = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(NUMBER_OF_RIDERS)]
    
    RIDER_COLOR = "#ff0000"
    RESTAURANT_COLOR = "#87005f"
    CUSTOMER_COLOR = "#875f00"
    GOLD_COLOR = "#EFE62F"

    CANCEL_INTERVAL = 600
    LOGGING_INTERVAL = 30

    TIME_UNIQUE = RIDER_LOCAITON_DF['time'].unique()
    NUMBER_OF_TIME_STEP = len(TIME_UNIQUE)


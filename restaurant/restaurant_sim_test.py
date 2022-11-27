# Cannot run due to circular import 
from restaurant_simulator import Restaurant, RestaurantSimulator
import pandas as pd

res_sim=RestaurantSimulator()

res_list = pd.read_csv("restaurant/restaurant_sample.csv")

for idx,res in res_list.iterrows():
    new_res=Restaurant([res["Merchant.Lat"],res["Merchant.Lng"]],res_sim.restaurant_idx,res["mean_preparing_time"],res["std_preparing_time"])
    res_sim.restaurant_idx+=1
    res_sim.restaurant_list.append(new_res)

print(res_sim.restaurant_list[0].location)
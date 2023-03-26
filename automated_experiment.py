import yaml
import os
from itertools import product

with open("./config.yaml", 'r') as stream:
    config_dict = yaml.safe_load(stream)
    
modes = ['batch']
rider_numebers = [10, 20]
time_windows = [300]
order_rate_factors = [1]

for m, rn, tw, orf in product(modes, rider_numebers, time_windows, order_rate_factors):
    config_dict['central_manager']['mode'] = m
    config_dict['rider']['number'] = rn
    config_dict['central_manager']['time_window'] = tw
    config_dict['order']['factor'] = orf

    with open('./config.yaml', 'w') as outfile:
        yaml.dump(config_dict, outfile)

    os.system("python main.py") 
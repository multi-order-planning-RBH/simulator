from scipy.optimize import milp, LinearConstraint, Bounds
from collections import defaultdict
import numpy as np
from math import ceil
from typing import Dict, List

import sys, os
sys.path.append(os.path.abspath("./"))
from rider.rider import Rider
from suggester.types.batch import Batch

def get_batch_to_rider(food_graph: Dict[Rider, Dict[Batch, int]]):
    batch_rider_pair_list = []
    count = 0 
    for k_r, v_r in food_graph.items():
        for k_b, v in v_r.items():
            batch_rider_pair_list.append([k_r, k_b, count, v])
            count += 1
    batch_rider_order_time_array = np.array(batch_rider_pair_list)
    return batch_rider_order_time_array

def solve_integer_programming(batch_rider_order_time_array): 
    rider_unique = set(batch_rider_order_time_array[:,0])
    len_rider = len(rider_unique)
    batch_unique = set(batch_rider_order_time_array[:,1])
    len_batch = len(batch_unique)
    len_A = len_rider+len_batch

    n = len(batch_rider_order_time_array)
    A = np.zeros((len_A, n))
    c = batch_rider_order_time_array[:,3]

    count = 0
    for rider in rider_unique:
        temp = batch_rider_order_time_array[:, 0] == rider 
        A[count, temp] = 1
        count += 1

    for batch in batch_unique:
        temp = batch_rider_order_time_array[:, 1] == batch 
        A[count, temp] = 1
        count += 1

    b_u = np.zeros_like(A[:, 0])
    b_l = np.zeros_like(b_u)

    u = np.full_like(A[0, :], 1)
    l = np.zeros_like(u)

    if len_rider < len_batch:
        temp = ceil(len_batch/len_rider)
        b_u[:len_rider] = temp
        b_u[len_rider:] = 2
        b_l[:len_rider] = temp
        b_l[len_rider:] = 1

    elif len_rider == len_batch:
        b_u[:] = 2
        b_l[:] = 2
    if len_rider > len_batch:
        temp = ceil(len_rider/len_batch)
        b_u[:len_rider] = 2
        b_u[len_rider:] = temp
        b_l[:len_rider] = 1
        b_l[len_rider:] = temp

    integrality = np.ones_like(batch_rider_order_time_array[:, 0])
    constraints = LinearConstraint(A, b_l, b_u)
    bounds = Bounds(lb = l, ub = u)
    res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)

    return res, rider_unique

def transform_res_to_graph(res, batch_rider_order_time_array, rider_unique):
    x = res.x
    selected_x = x == 1
    selected_pair = batch_rider_order_time_array[selected_x][:, :2]

    suggested_rider_batch_graph = defaultdict(list)
    for rider in rider_unique:
        selected_batch = selected_pair[selected_pair[:, 0] == rider, :][:, 1]
        for batch in selected_batch:
            suggested_rider_batch_graph[rider].append(batch)

    return suggested_rider_batch_graph

def rider_suggester(food_graph: Dict[Rider, Dict[Batch, int]]) -> Dict[Rider, List[Batch]]:
    batch_rider_order_time_array = get_batch_to_rider(food_graph)
    res, rider_unique = solve_integer_programming(batch_rider_order_time_array)
    suggested_rider_batch_graph = transform_res_to_graph(res, batch_rider_order_time_array, rider_unique)
    return suggested_rider_batch_graph

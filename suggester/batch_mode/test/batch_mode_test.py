import sys, os
sys.path.append(os.path.abspath("./"))

from suggester.batch_mode.batch_mode import batchmode
from order_restaurant.order_restaurant_simulator import order_simulator
from rider.rider import Rider

riders = [Rider(i) for i in range(5)]
for i in range(10):
    order_simulator.simulate(i)
orders = [o for o in order_simulator.order_dict.values()]

order_graph, edge_list, batches, food_graph, suggested_rider_batch_graph = batchmode.suggest(orders, riders, 10, for_test = True)

print(order_graph, "\n")
print(edge_list, "\n")
print(batches, "\n")
print(food_graph, "\n")
print(suggested_rider_batch_graph, "\n")

for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        print(riders.index(r), batches.index(b), food_graph[r][b])

print(len(batches))

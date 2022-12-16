import sys, os
sys.path.append(os.path.abspath("./"))

from rider.rider import Rider
from suggester.batch_mode.batch import Batch
from suggester.batch_mode.rider_suggester import rider_suggester

# Case 1 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(3)]
batches = [Batch() for _ in range(3)]
weights = [[1, 2, 100],
            [100, 1, 2],
            [1, 100, 2]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_order_rider_graph = rider_suggester(food_graph)
print(suggested_order_rider_graph)



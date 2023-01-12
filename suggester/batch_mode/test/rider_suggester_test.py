import sys, os
sys.path.append(os.path.abspath("./"))

from rider.rider import Rider
from suggester.types.batch import Batch
from suggester.batch_mode.batch_mode import batchmode

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
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        if food_graph[r][b] == 100:
            assert False


# Case 2 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(5)]
batches = [Batch() for _ in range(3)]
weights = [[1, 100, 100],
            [1, 2, 100],
            [100, 1, 100],
            [100, 100, 1],
            [100, 100, 1]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        if food_graph[r][b] == 100:
            assert False


# Case 3 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(3)]
batches = [Batch() for _ in range(5)]
weights = [[1, 2, 100, 100, 100],
            [100, 100, 1, 2, 100],
            [100, 100, 100, 1, 2]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        if food_graph[r][b] == 100:
            assert False

# Case 4 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(3)]
batches = [Batch() for _ in range(3)]
weights = [[1, 2, 1],
            [2, 1, 2],
            [1, 1, 2]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

"""for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        print(riders.index(r), batches.index(b), food_graph[r][b])"""


# Case 5 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(7)]
batches = [Batch() for _ in range(3)]
weights = [[2, 3, 4],
            [4, 3, 2],
            [2, 3, 4],
            [4, 3, 2],
            [2, 3, 4],
            [4, 3, 2],
            [2, 3, 4]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

"""print()
for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        print(riders.index(r), batches.index(b), food_graph[r][b])"""

# Case 6 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

food_graph = {}

riders = [Rider(i) for i in range(2)]
batches = [Batch() for _ in range(7)]
weights = [[1, 2, 2, 2, 3, 2, 1],
            [2, 2, 1, 2, 3, 2, 1],
            [2, 2, 2, 1, 3, 2, 1]]

for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

"""print()
for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        print(riders.index(r), batches.index(b), food_graph[r][b])"""


# Case 7 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

import numpy as np

food_graph = {}

riders = [Rider(i) for i in range(10)]
batches = [Batch() for _ in range(20)]

weights = np.random.random_sample((10, 20))


for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

"""print()
print(weights)
print()
for r in suggested_rider_batch_graph:
    for b in suggested_rider_batch_graph[r]:
        print(riders.index(r), batches.index(b), food_graph[r][b])"""

# Case 7 - Test trivial case in equal size sets of riders and batches, 
# specify unselected edge by heavy weight.

import numpy as np

food_graph = {}

riders = [Rider(i) for i in range(20)]
batches = [Batch() for _ in range(10)]

weights = np.random.random_sample((20, 10))


for i, r in enumerate(riders):
    food_graph[r] = {}
    for j, b in enumerate(batches):
        food_graph[r][b] = weights[i][j]
        
suggested_rider_batch_graph = batchmode.rider_suggester(food_graph)

"""print()
print(weights)
print()"""
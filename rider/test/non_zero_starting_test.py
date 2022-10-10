from argparse import Action
import sys, os
sys.path.append(os.path.abspath("./"))

from rider.rider import Rider, Order
from common.action import ActionEnum
from common.location import Coordinates

id = 0
startingTime = 100
getoffTime = 480
restingTime = 30

rider = Rider(id, startingTime , getoffTime, restingTime)

resraurant_location = Coordinates(13.744740, 100.531876)
destination_location = Coordinates(13.744740, 100.531876)
created_time = 110
ready_time = 150

order = Order(destination_location, resraurant_location, 1, created_time, ready_time)

assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status"

rider.simulate(10)
assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status after passing 10 mins"

rider.simulate(50)
assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status after passing 50 mins"

rider.simulate(99)
assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status after passing 99 mins"

rider.simulate(100)
assert_statement = rider.current_action.action == ActionEnum.NO_ACTION
assert assert_statement, "Should be the rider holding NO_ACTION status after passing 100 mins"

rider.add_order_destination(order, 110)
rider.simulate(110)
assert_statement = rider.current_action.action == ActionEnum.NO_ACTION and \
                    rider.next_action.action == ActionEnum.RIDING and \
                    len(rider.destinations) == 2
assert assert_statement, "Should be the rider holding NO_ACTION status and being prepared for next order at 110 mins"

rider.simulate(111)
assert_statement = rider.current_action.action == ActionEnum.RIDING and \
                    len(rider.destinations) == 2 and \
                    rider.current_action.time == 111 and \
                    rider.next_action.action == ActionEnum.WAITING and \
                    rider.next_action.time == 141 and \
                    rider.destinations[0].location == resraurant_location

assert assert_statement, "Should be the rider holding RIDING status at 111 mins"

rider.simulate(141)
assert_statement = rider.current_action.action == ActionEnum.WAITING and \
                    len(rider.destinations) == 2 and \
                    rider.current_action.time == 141 and \
                    rider.next_action.action == ActionEnum.PICKUP_OR_DELIVER and \
                    rider.next_action.time == 151 and \
                    rider.destinations[0].location == resraurant_location
assert assert_statement, "The rider should be holding Waiting status at 141 mins"

rider.simulate(150)
assert_statement = rider.current_action.action == ActionEnum.WAITING 
assert assert_statement, "Should be the rider holding WAITING status after passing 150 mins"

rider.simulate(151)
assert_statement = rider.current_action.action == ActionEnum.PICKUP_OR_DELIVER and \
                    len(rider.destinations) == 1 and \
                    rider.current_action.time == 151 and \
                    rider.next_action.action == ActionEnum.RIDING and \
                    rider.next_action.time == 152 and \
                    rider.destinations[0].location == destination_location
assert assert_statement, "The rider should be holding PICKUP status at 151 mins"

rider.simulate(152)
assert_statement = rider.current_action.action == ActionEnum.RIDING and \
                    len(rider.destinations) == 1 and \
                    rider.current_action.time == 152 and \
                    rider.next_action.action == ActionEnum.WAITING and \
                    rider.next_action.time == 182 and \
                    rider.destinations[0].location == destination_location
assert assert_statement, "The rider should be holding RIDING status at 152 mins"

for time in range(153,182):
    rider.simulate(time)

rider.simulate(182)
assert_statement = rider.current_action.action == ActionEnum.WAITING and \
                    len(rider.destinations) == 1 and \
                    rider.current_action.time == 182 and \
                    rider.next_action.action == ActionEnum.PICKUP_OR_DELIVER and \
                    rider.next_action.time == 188 and \
                    rider.destinations[0].location == destination_location and \
                    float(rider.location-rider.destinations[0].location) < 0.0001
assert assert_statement, "The rider should be holding WAITING status at 182 mins"
print("[/] Pass - Location estimation.")

rider.resting_prob = 1

rider.simulate(188)
assert_statement = rider.current_action.action == ActionEnum.PICKUP_OR_DELIVER and \
                    len(rider.destinations) == 0 and \
                    rider.current_action.time == 188 and \
                    rider.next_action.action == ActionEnum.NO_ACTION and \
                    rider.next_action.time == 189 
assert assert_statement, "The rider should be holding PICKUP_OR_DELIVER status at 188 mins"

rider.simulate(189)
assert_statement = rider.current_action.action == ActionEnum.NO_ACTION and \
                    len(rider.destinations) == 0  
assert assert_statement, "The rider should be holding NO_ACTION status at 189 mins"

rider.simulate(190)
assert_statement = rider.current_action.action == ActionEnum.NO_ACTION and \
                    len(rider.destinations) == 0  and \
                    rider.next_action.action == ActionEnum.RESTING and \
                    rider.next_action.time == 191
                    
assert assert_statement, "The rider should be holding NO_ACTION status at 190 mins"

rider.simulate(191)
assert_statement = rider.current_action.action == ActionEnum.RESTING and \
                    rider.current_action.time == 191 and \
                    len(rider.destinations) == 0  and \
                    rider.next_action.action == ActionEnum.NO_ACTION and \
                    rider.next_action.time == 221
                    
assert assert_statement, "The rider should be holding RESTING status at 191 mins"

rider.resting_prob = 0.01

rider.simulate(221)
assert_statement = rider.current_action.action == ActionEnum.NO_ACTION and \
                    rider.current_action.time == 221 and \
                    len(rider.destinations) == 0 
                    
assert assert_statement, "The rider should be holding NO_ACTION status at 221 mins"

rider.simulate(480)
assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status after passing 480 mins"

rider.simulate(481)
assert_statement = rider.current_action.action == ActionEnum.UNAVAILABLE
assert assert_statement, "Should be the rider holding UNAVAILABLE status after passing 480 mins"

print("[/] Pass - non zero starting time initializing.")
print("[/] Pass - rider assigning.")
print("[/] Pass - rider resting.")
print("[/] Pass - rider getting off.")

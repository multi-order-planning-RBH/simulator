from rider.rider import Rider, TempOrder
from common.action import ActionEnum

id = 0
startingTime = 0
getoffTime = 480
restingTime = 30

rider = Rider(id, startingTime , getoffTime, restingTime)

resraurantLocation = [13.744740, 100.531876]
destination = [13.741291, 100.528645]
orderTime = 0
readyTime = 30
order = TempOrder(resraurantLocation, destination, orderTime, readyTime)

rider.add_order_destination(order)
assert len(rider.destinations) == 2, "Should be two places being added to destinations of the rider"
assert rider.current_action.action == ActionEnum.NO_ACTION, "Should be the rider holding NO_ACTION status"
print("Passed for the first order adding")

time = 0
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.NO_ACTION and \
    rider.current_action.time == 0 and \
    rider.next_action.action == ActionEnum.RIDING and \
    rider.next_action.time == 1
assert assessment, "Should be the rider doing nothing at 0 timeunit and riding to the restaurant at 1 timeunit"
print("Passed at 0 timeunit")

time = 1
rider.simulate(time)
assessment =  rider.current_action.action == ActionEnum.RIDING and \
    rider.current_action.time == 1 and \
    rider.next_action.action == ActionEnum.WAITING and \
    rider.next_action.time == 31 and \
    rider.destinations[0].location == resraurantLocation
assert assessment, "Should be the rider riding at 1 timeunit and arriving at the restaurant at 31 timeunits"
print("Passed at 1 timeunits")

time = 31
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.WAITING and \
    rider.current_action.time == 31 and \
    rider.next_action.action == ActionEnum.PICKUP_OR_DELIVER and \
    rider.next_action.time == 32
assert assessment, "Should be the rider arriving at the restaurant at 31 timeunits and picking up at 32 timeunits"
print("Passed at 31 timeunits")

time = 32
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.PICKUP_OR_DELIVER and \
    rider.current_action.time == 32 and \
    rider.next_action.action == ActionEnum.NO_ACTION and \
    rider.next_action.time == 33
assert assessment, "Should be the rider picking up at 32 timeunits and doing nothing at 33 timeunits"
print("Passed at 32 timeunits")

time = 33
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.NO_ACTION and\
    rider.current_action.time == 33 and \
    rider.next_action == None
assert assessment, "Should be the rider doing nothing at 33 timeunits"
print("Passed at 33 timeunits")

time = 34
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.NO_ACTION and \
    rider.next_action.action == ActionEnum.RIDING and \
    rider.next_action.time == 35 and\
    rider.destinations[0].location == destination
assert assessment , "Should be the rider doing nothing at 34 timeunits and riding toward the destination at 35 timeunits"
print("Passed at 34 timeunits")

time = 35
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.RIDING and \
    rider.current_action.time == 35 and \
    rider.next_action.action == ActionEnum.WAITING and \
    rider.next_action.time == 65
assert assessment , "Should be the rider riding toward the destination at 35 timeunits and reaching the destination at 65 timeunits"
print("Passed at 35 timeunits")

time = 65
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.WAITING and \
    rider.current_action.time == 65 and \
    rider.next_action.action == ActionEnum.PICKUP_OR_DELIVER and \
    rider.next_action.time == 71
assert assessment , "Should be the rider reaching the destination at 65 timeunits and delivering the order at 71 timeunits"
print("Passed at 65 timeunits")

time = 71
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.PICKUP_OR_DELIVER and \
    rider.current_action.time == 71 and \
    rider.next_action.action == ActionEnum.NO_ACTION and \
    rider.next_action.time == 72
assert assessment , "Should be the rider delivering the order at 71 timeunits and doing nothing at 72 timeunits"
print("Passed at 71 timeunits")

time = 72
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.NO_ACTION and \
    rider.current_action.time == 72 and \
    rider.next_action == None
assert assessment , "Should be rider doing nothing at 72 timeunits"
print("Passed at 72 timeunits")

time = 73
rider.simulate(time)
assessment = rider.current_action.action == ActionEnum.NO_ACTION and \
    rider.next_action == None
assert assessment , "Should be rider doing nothing at 73 timeunits"
print("Passed at 73 timeunits")

resraurantLocation = [13.744740, 100.531876]
destination = [13.741291, 100.528645]
orderTime = 0
readyTime = 120
order = TempOrder(resraurantLocation, destination, orderTime, readyTime)

rider.add_order_destination(order)
assert len(rider.destinations) == 2, "Should be two places being added to destinations of the rider"
assert rider.current_action.action == ActionEnum.NO_ACTION, "Should be the rider holding NO_ACTION status"
print("Passed for adding the second order")

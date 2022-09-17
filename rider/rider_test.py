from rider import Rider, TempOrder
from type_enum.location import LocationType, LocationEnum, generateBangkokLocation
from type_enum.action import ActionEnum
from type_enum.status import StatusEnum

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
assert rider.currentAction.action == ActionEnum.NO_ACTION, "Should be the rider holding NO_ACTION status"

#Journey starting
time = 0
rider.simulate(time)
assessment = rider.nextAction.action == ActionEnum.RIDING and rider.nextAction.time == 1
print(rider.nextAction.action, rider.nextAction.time)
assert assessment, "Should be the rider riding at 0 timeunit"

#Still riding
time = 1
rider.simulate(time)
assessment = rider.nextAction.action == ActionEnum.WAITING and rider.nextAction.time == 31
print(rider.nextAction.action, rider.nextAction.time)
assert assessment, "Should be the rider riding at 10 timeunits"

#Reach the restaurant and pick up
time = 31
rider.simulate(time)
assessment = rider.nextAction.action == ActionEnum.PICKUP_OR_DELIVER and rider.nextAction.time == 32
print(rider.nextAction.action, rider.nextAction.time)
assert assessment , "Should be the rider waiting at the restaurant at 31 timeunits"


#Picked up
time = 32
rider.simulate(time)
assessment = rider.nextAction.action == ActionEnum.NO_ACTION
print(rider.nextAction.action, rider.nextAction.time)
assert assessment , "Should be the rider not owning any task at 32 timeunits"

#Picked up
time = 33
rider.simulate(time)
assessment = rider.nextAction == None 
print(rider.currentAction.action, rider.currentAction.time)

time = 34
rider.simulate(time)
assessment = rider.nextAction == None 
print(rider.nextAction.action, rider.nextAction.time)

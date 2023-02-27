# ML
from shapely.geometry import Point
import pickle as pkl
import numpy as np
from math import * 
from sklearn.ensemble import GradientBoostingRegressor
from ml_estimator.distance_calculator import DistanceCalculator
import warnings
warnings.filterwarnings("ignore")


class DeliveryModel: 
    def __init__(self):
        self.model = pkl.load(open('ml_estimator/gbdt_m_delivery.pkl', 'rb'))
        self.distanceCalculator = DistanceCalculator()
        self.dayMap = {"MON":0, "TUE":1, "WED":2, "THU":3, "FRI":4, "SAT":5, "SUN":6}

    def get_euc(self, coords_1, coords_2):
        R = 6371000
        conversion_const = 0.0174533
        c_1 = coords_1*conversion_const
        c_2 = coords_2*conversion_const
        delta_phi = abs(c_1[:,1]-c_2[:,1])
        theta = c_1[:,0]
        delta_theta = abs(c_1[:,0]-c_2[:,0])
        del_x = R*np.cos(theta)*delta_phi 
        del_y = R*delta_theta
        return np.sqrt(del_x**2 + del_y**2)
    
    def batch_predict(self, locations, day_of_week=[], approx=True):
        '''
        input:
        - locations = numpy array [(u_i,v_i) | i] where u_i = (lat,long) of the start location, 
        v_i = (lat_long) of the destination location 
        - (optional) day_of_week = numpy array [day_i | i] : choose one of these -> "MON", "TUE, "WED", "THU", "FRI", "SAT", "SUN"
        
        output:
        - The array prediction of the duration in minute (m) needed to travel from point u to point v 
        (please note that if you want to predict the duration needed from rider currently at point x and need to pick up food at point y and deliver at point z, you need to calculate the time it takes for x to go to y and the time it takes from a rider to from y to z)
        
        Note: 
        - When you set 'approx' to True, the model will approximate certain input feature for the sake of performance (speed) of prediction.
        - When you set 'approx' to False, the model will compute certain input feature more accurately but in expense of the speed of the prediciton.
        
        '''
        n = len(locations)
        idx = np.arange(0,n)
        if len(day_of_week) != n : 
            day_of_week = np.full(n,"MON")
        u = np.apply_along_axis(lambda loc_i : loc_i[0], axis=1, arr=locations)
        v = np.apply_along_axis(lambda loc_i : loc_i[1], axis=1, arr=locations)
        
        merchant_lat = np.apply_along_axis(lambda u_i : u_i[0], axis=1, arr=u)
        merchant_long = np.apply_along_axis(lambda u_i : u_i[1], axis=1, arr=u)
        
        customer_lat = np.apply_along_axis(lambda v_i : v_i[0], axis=1, arr=v)
        customer_long = np.apply_along_axis(lambda v_i : v_i[1], axis=1, arr=v)
    
        f = (lambda idx: self.get_euc(coords_1=u[idx], coords_2=v[idx]))
        
        EucDist = f(idx)
        if approx : 
            ShortestDist = EucDist.copy()*1.2
        else :
            ShortestDist = [self.distanceCalculator.shortestDistance(u[i],v[i]) for i in range(n)]

        u,inv = np.unique(day_of_week, return_inverse = True)
        day_inverse = np.array([self.dayMap[x] for x in u])[inv].reshape(day_of_week.shape)
        day_of_week_sin = np.apply_along_axis(lambda day : np.sin(day*(2.*np.pi/7)) , axis=0, arr=day_inverse)
        day_of_week_cos = np.apply_along_axis(lambda day : np.cos(day*(2.*np.pi/7)) , axis=0, arr=day_inverse)
        
        X = np.column_stack((merchant_lat, merchant_long, customer_lat, customer_long, EucDist, ShortestDist, day_of_week_sin, day_of_week_cos))
        return self.model.predict(X)
    
estimator = DeliveryModel()

def estimate_traveling_time(start: Point, stop: Point) -> int:

    model_input = np.array([[[start.y,start.x],[stop.y,stop.x]]])
    
    return int(estimator.batch_predict(model_input)[0]*60)
    # return 600


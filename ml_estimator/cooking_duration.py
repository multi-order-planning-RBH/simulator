# ML
import scipy
import pickle as pkl
import numpy as np
from math import * 
from ml_estimator.distance_calculator import DistanceCalculator 
import pandas as pd 
from sklearn.ensemble import GradientBoostingRegressor

class FoodPrepModel: 
    def __init__(self):
        self.model = pkl.load(open('ml_estimator/food_preparation_best_gbdt_m.pkl', 'rb'))
        self.deliveryML = pkl.load(open('ml_estimator/food_delivery_best_gbdt_m.pkl', 'rb'))      
        self.distanceCalculator = DistanceCalculator()
        self.dayMap = {"MON":0, "TUE":1, "WED":2, "THU":3, "FRI":4, "SAT":5, "SUN":6}
        self.NationFoodCategories = ['NationFoodCategory_International',
                                    'NationFoodCategory_Isram',
                                    'NationFoodCategory_Japanese',
                                    'NationFoodCategory_Korean',
                                    'NationFoodCategory_Myanmar',     
                                    'NationFoodCategory_Thai',         
                                    'NationFoodCategory_Vietnam'
                                    ]
        self.FoodCategories = [
            'FoodCategories_FastFood',
        'FoodCategories_QuickMeal',
        'FoodCategories_ขนมจีน',
        'FoodCategories_ของหวาน',                  
        'FoodCategories_ปิ้งย่าง',
        'FoodCategories_พิซซ่า',                     
        'FoodCategories_ร้านก๋วยเตี๋ยว',               
        'FoodCategories_ร้านอาหาร',                 
        'FoodCategories_สปาเก็ตตี้',                  
        'FoodCategories_สุกี้ยากี้',
        'FoodCategories_สเต๊ก',                     
        'FoodCategories_อาหารคลีน',                 
        'FoodCategories_อาหารจานด่วน',              
        'FoodCategories_อาหารตามสั่ง',               
        'FoodCategories_อาหารทะเล',                
        'FoodCategories_อาหารอีสาน',                
        'FoodCategories_อาหารฮาลาล',               
        'FoodCategories_อาหารเหนือ',                
        'FoodCategories_อาหารใต้',                  
        'FoodCategories_เครื่องดื่ม',                  
        'FoodCategories_ไก่ทอด'
        ]
        self.col = [
        "Merchant_lat",
        "Merchant_lon",                  
        'NationFoodCategory_International',
        'NationFoodCategory_Isram',
        'NationFoodCategory_Japanese',
        'NationFoodCategory_Korean',
        'NationFoodCategory_Myanmar',     
        'NationFoodCategory_Thai',         
        'NationFoodCategory_Vietnam',
        'FoodCategories_FastFood',
        'FoodCategories_QuickMeal',
        'FoodCategories_ขนมจีน',
        'FoodCategories_ของหวาน',                  
        'FoodCategories_ปิ้งย่าง',
        'FoodCategories_พิซซ่า',                     
        'FoodCategories_ร้านก๋วยเตี๋ยว',               
        'FoodCategories_ร้านอาหาร',                 
        'FoodCategories_สปาเก็ตตี้',                  
        'FoodCategories_สุกี้ยากี้',
        'FoodCategories_สเต๊ก',                     
        'FoodCategories_อาหารคลีน',                 
        'FoodCategories_อาหารจานด่วน',              
        'FoodCategories_อาหารตามสั่ง',               
        'FoodCategories_อาหารทะเล',                
        'FoodCategories_อาหารอีสาน',                
        'FoodCategories_อาหารฮาลาล',               
        'FoodCategories_อาหารเหนือ',                
        'FoodCategories_อาหารใต้',                  
        'FoodCategories_เครื่องดื่ม',                  
        'FoodCategories_ไก่ทอด',
        "riderInitial_to_Merchant_EucDistance",
        "riderInitial_to_Merchant_ShortestDistance",
        "day_of_week_sin",                                           
        "day_of_week_cos",                                          
        "calledMerchantTime_to_arrivedAtMerchantTime_prediction (m)"]

        self.col_prime = ["u_lat", "u_lon", "v_lat", "v_lon","euc_dist","shortest_dist" ,"day_of_week_sin" ,"day_of_week_cos"]

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
    
    def batch_predict(self, locations, day_of_week=[], NationFoodCategory=[], FoodCategory = [], approx=True):
        '''
        input:
        - locations = numpy array [(u_i,v_i) | i] where u_i = (lat,long) of the rider location, 
        v_i = (lat_long) of the merchant location 
        - (optional) day_of_week = numpy array [day_i | i] : choose one of these -> "MON", "TUE, "WED", "THU", "FRI", "SAT", "SUN"
        - (optional) NationFoodCategory = numpy array [N_i | i] : choose one of the strings in self.NationFoodCategories (in __init__)
        - (optional) FoodCategory = numpy array [F_i | i] : choose one of the strings in self.FoodCategories (in __init__)
        
        output:
        - The array of predictions of the duration in minute (m) needed for a rider to travel from their position to merchant finishing their preparation
        
        Note: 
        - When you set 'approx' to True, the model will approximate certain input feature for the sake of performance (speed) of prediction.
        - When you set 'approx' to False, the model will compute certain input feature more accurately but in expense of the speed of the prediciton.
        
        '''
 
        n = len(locations)
        idx = np.arange(0,n)
        if len(day_of_week) != n : 
            day_of_week = np.full(n,"MON")
        if len(NationFoodCategory) != n : 
            NationFoodCategory = np.full(n,"NationFoodCategory_International")
        if len(FoodCategory) != n : 
            FoodCategory = np.full(n,'FoodCategories_FastFood')
            
        u = np.apply_along_axis(lambda loc_i : loc_i[0], axis=1, arr=locations)
        v = np.apply_along_axis(lambda loc_i : loc_i[1], axis=1, arr=locations)
        
        rider_lat = np.apply_along_axis(lambda u_i : u_i[0], axis=1, arr=u)
        rider_long = np.apply_along_axis(lambda u_i : u_i[1], axis=1, arr=u)
        
        merchant_lat = np.apply_along_axis(lambda v_i : v_i[0], axis=1, arr=v)
        merchant_long = np.apply_along_axis(lambda v_i : v_i[1], axis=1, arr=v)
    
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
        
        N = [] 
        for s in self.NationFoodCategories : 
            tmp = np.apply_along_axis(lambda t: (t == s), axis = 0, arr=NationFoodCategory).astype(int)
            N.append(tmp)
        
        F = []
        for s in self.FoodCategories : 
            tmp = np.apply_along_axis(lambda t: (t==s), axis = 0, arr=FoodCategory).astype(int)
            F.append(tmp)
        
        X_prime = np.column_stack((rider_lat, rider_long, merchant_lat, merchant_long, EucDist, ShortestDist, day_of_week_sin, day_of_week_cos))
        X_prime = pd.DataFrame(X_prime, columns=self.col_prime)
        pred_fea = self.deliveryML.predict(X_prime) 
        
        X = np.column_stack((merchant_lat,merchant_long,*N,*F,EucDist,ShortestDist,
                            day_of_week_sin,day_of_week_cos,pred_fea))
        X = pd.DataFrame(X, columns=self.col)
        return self.model.predict(X)

foodprep_model = FoodPrepModel()

def estimate_cooking_duration(order,location) -> int:
    # tmp wait for ML
    
    location = np.array([[[location.y,location.x],[location.y,location.x]]])

    day_of_week = []
    NationFoodCategory=[order.food_nation]
    FoodCategory = [order.food_category]

    return foodprep_model.batch_predict(location,day_of_week,NationFoodCategory,FoodCategory)[0]*60
    # mean =1000
    # std=300

    # lower_bound = 200
    # upper_bound = 2500

    # cooking_duration = int(scipy.stats.truncnorm.rvs((lower_bound-mean)/std,
    #                                     (upper_bound-mean)/std,
    #                                     loc=mean,scale=std,size=1)[0])
    # if cooking_duration<=0:
    #     cooking_duration = 1000
    # return cooking_duration
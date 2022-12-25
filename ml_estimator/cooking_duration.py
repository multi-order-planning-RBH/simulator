# ML
import scipy
def estimate_cooking_duration(order) -> int:
    # tmp wait for ML
    mean =1000
    std=300

    lower_bound = 200
    upper_bound = 2500

    cooking_duration = int(scipy.stats.truncnorm.rvs((lower_bound-mean)/std,
                                        (upper_bound-mean)/std,
                                        loc=mean,scale=std,size=1)[0])
    if cooking_duration<=0:
        cooking_duration = 1000
    return cooking_duration
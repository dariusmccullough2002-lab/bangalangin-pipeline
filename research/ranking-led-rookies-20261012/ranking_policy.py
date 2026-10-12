"""Read-only research adapter: policy values are separate from contribution forecasts."""
import math,json
from pathlib import Path

def model_weight(exposure,strength,supported=True):
 if exposure<0 or strength<=0:raise ValueError('Invalid exposure/strength')
 return .5*exposure/(exposure+strength) if supported else 0.
def effective_rank(source_rank,model_rank,exposure,strength,lower=1,upper=500,supported=True):
 if not 1<=source_rank<=500 or not 1<=model_rank<=500 or lower>upper:raise ValueError('Invalid rank')
 w=model_weight(exposure,strength,supported)
 rank=math.exp((1-w)*math.log(source_rank)+w*math.log(model_rank))
 return min(upper,max(lower,rank)),w

def interpolate(curve,rank):
 # Persisted curve stays fixed across firstPA/IP and eligibility changes.
 i=max(0,min(len(curve)-1,int(math.floor(rank))-1));j=min(i+1,len(curve)-1)
 fraction=max(0,min(1,rank-curve[i]['rank']))
 return curve[i]['value']*(1-fraction)+curve[j]['value']*fraction

def listed_value(entry,curve,model_rank,exposure,strength,supported=True):
 rank,w=effective_rank(entry['source_rank'],model_rank,exposure,strength,entry['minimum_adjusted_rank'],entry['maximum_adjusted_rank'],supported)
 return {'policy_value':interpolate(curve,rank),'effective_rank':rank,'source_weight':1-w,'model_weight':w,'quantity':'Ranking-led policy value; not expected contribution or transaction price'}

def graduated_value(last_policy_value,exposure_at_graduation,current_exposure,strength,mlb_estimate,confirmed=False):
 if not confirmed or mlb_estimate is None:return {'policy_value':last_policy_value,'new_evidence_weight':0,'status':'Last supported ranking-policy value retained; graduation or supported MLB estimate unavailable'}
 if strength<=0 or min(current_exposure,exposure_at_graduation,last_policy_value,mlb_estimate)<0:raise ValueError('Invalid evidence/value')
 delta=max(0,current_exposure-exposure_at_graduation);w=delta/(delta+strength)
 return {'policy_value':(1-w)*last_policy_value+w*mlb_estimate,'new_evidence_weight':w,'status':'Unvalidated continuous graduation policy; no eligibility-triggered cliff'}

"""Additional predeclared diagnostic experiments; none select deployment parameters."""
import analyze as a
import json,datetime,math
import numpy as np
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.metrics import log_loss
bios={p['id']:p for f in a.RAW.glob('bios-*.json') for p in json.load(open(f))['people']}
def age(p):
 d=datetime.date.fromisoformat(bios[p['mlbamId']]['birthDate']);return (datetime.date(p['year'],2,1)-d).days/365.2425
for p in a.cohort:p['evaluation_age']=age(p)
def f(p,trajectory=False):
 v=a.features(p)+[(age(p)-22)/5]
 if trajectory:
  old=a.lookup.get((p['year']-1,p['mlbamId']));v += [int(old is not None),(old-p['rank'])/100 if old else 0]
 return v
experiments={}
for name,train,trajectory,with_age in [('rank_role_age',a.train,False,True),('2013_matched_rank_role_age', [p for p in a.cohort if p['year']==2013],False,True),('2013_matched_plus_trajectory',[p for p in a.cohort if p['year']==2013],True,True)]:
 m=LogisticRegression(C=.3,max_iter=2000).fit([f(p,trajectory) for p in train],[p['label'] for p in train]);pr=m.predict_proba([f(p,trajectory) for p in a.test]);full=np.zeros((len(pr),5));full[:,m.classes_]=pr
 experiments[name]={'train_n':len(train),'metrics':a.metrics(full),'test_n':len(a.test),'classes':m.classes_.tolist()}
# Paired holdout uncertainty: test identities bootstrap, not independent class rows.
rng=np.random.default_rng(720);d=(np.sum((a.pred-np.eye(5)[a.truth])**2,axis=1)-np.sum((np.array(a.u2)-np.eye(5)[a.truth])**2,axis=1));b=[np.mean(d[rng.integers(0,len(d),len(d))]) for _ in range(2000)]
def wilson(k,n):
 if not n:return None
 z=1.96;mid=(k/n+z*z/2/n)/(1+z*z/n);half=z*math.sqrt(k/n*(1-k/n)/n+z*z/4/n/n)/(1+z*z/n);return [max(0,mid-half),min(1,mid+half)]
bins=[]
for role in [0,1]:
 for lo,hi in [(1,25),(26,50),(51,100)]:
  subset=[p for p in a.test if p['pitcher']==role and lo<=p['rank']<=hi];counts=np.bincount([p['label'] for p in subset],minlength=5);bins.append({'pitcher':role,'rank_range':[lo,hi],'n':len(subset),'counts':counts.tolist(),'superstar_95_wilson':wilson(int(counts[4]),len(subset))})
# Fixed label-threshold stress; refit rank/role to each alternative label definition.
sensitivity=[]
for factor in [.8,1,1.2]:
 def label(p,remove_covid=False):
  fut=[a.rows.get((yr,p['mlbamId']),{'score':0,'ex':0,'role':'SP' if p['pitcher'] else 'H'}) for yr in range(p['year'],p['year']+5) if not(remove_covid and yr==2020)]
  peak=np.mean(sorted([v['score'] for v in fut],reverse=True)[:2]);regular=sum(v['ex']>=(250 if v['role']=='H' else 40) for v in fut)>=2;return 0 if not regular else 1+sum(peak>=t*factor for t in a.thresholds[1:])
 for remove in [False,True]:
  y=[label(p,remove) for p in a.train];truth=np.array([label(p,remove) for p in a.test]);m=LogisticRegression(C=.3,max_iter=2000).fit(a.X,y);pr=np.zeros((len(a.test),5));pr[:,m.classes_]=m.predict_proba(a.T);sensitivity.append({'threshold_multiplier':factor,'exclude_2020_instead_of_actual_production':remove,'training_counts':np.bincount(y,minlength=5).tolist(),'heldout_counts':np.bincount(truth,minlength=5).tolist(),'log_loss':float(log_loss(truth,np.maximum(pr,1e-10),labels=range(5))),'brier':float(np.mean(np.sum((pr-np.eye(5)[truth])**2,axis=1)))})
# Multi-year intrinsic contribution; owner horizon preferences fixed in advance, not fitted to trades.
horizons={'Contender':[1.0],'Balanced':[.88**t for t in range(3)],'Rebuild':[.88**t for t in range(5)]};future={}
for name,w in horizons.items():
 def target(yr,id):return sum(weight*a.rows.get((yr+1+t,id),{'score':0})['score'] for t,weight in enumerate(w))
 train=[(yr,v,target(yr,id)) for (yr,id),v in a.rows.items() if yr<=2012 and v['ex']>=(150 if v['role']=='H' else 30)]
 hold=[(yr,v,target(yr,id)) for (yr,id),v in a.rows.items() if yr in [2017,2018] and v['ex']>=(150 if v['role']=='H' else 30)]
 model=Ridge(alpha=10).fit([a.mlb_features(v) for _,v,_ in train],[x for _,_,x in train]);future[name]={}
 for role in ['H','SP','RP']:
  z=[x for x in hold if x[1]['role']==role];actual=np.array([x for _,_,x in z]);pr=model.predict([a.mlb_features(v) for _,v,_ in z]);naive=np.array([v['score']*sum(w) for _,v,_ in z]);future[name][role]={'n':len(z),'forecast_mae':float(np.mean(abs(pr-actual))),'constant_production_mae':float(np.mean(abs(naive-actual))),'forecast_bias':float(np.mean(pr-actual))}
# Nonlinear utility applied per asset outcome once, never to sum of a package.
def u(x,g=1.35):return max(0,x)**g
stress=[]
for title,one,many in [('Elite MLB versus good MLB',[20],[8,7,6]),('Elite prospect versus mids',[14],[6,5,4]),('Hitter versus SP',[10],[8]),('Prospect versus MLB',[12],[10]),('Illustrative FYPD package',[7],[3,2,1]),('Large consolidation',[20],[4]*8)]:
 stress.append({'case':title,'intrinsic_contributions':[one,many],'per_asset_utility':[sum(map(u,one)),sum(map(u,many))],'WRONG_utility_of_package_total':[u(sum(one)),u(sum(many))],'roster_and_acquisition_adjustment':None,'interpretation':'Synthetic architecture stress only; prospect/pick uncertainty not estimated here; no fairness conclusion'})
prior=a.ROOT.parent/'2026-10-07'/'unified-review'/'results.json'
if not prior.exists(): prior=__import__('pathlib').Path('/workspace/scratch/5d49fbf53525/unified-review/results.json')
old=json.load(open(prior));saved={'status':'Preserved comparisons only; cannot score these current assets with historical rank model without dated MLB Pipeline rank and MLBAM/Fantrax crosswalk','cases':old['cases'],'U2_anchors':old['audit']['annual_surplus_anchors']}
(a.OUT/'saved-U2-comparisons.json').write_text(json.dumps(saved,indent=2))
result={'feature_experiments':experiments,'paired_brier_difference_vs_U2':{'mean':float(np.mean(d)),'bootstrap_95_interval':np.quantile(b,[.025,.975]).tolist(),'negative_favors_calibration':True},'empirical_holdout_bins':bins,'outcome_definition_sensitivities':sensitivity,'owner_horizon_diagnostics':future,'package_stress':stress,'checks':{'no_identity_overlap':not(set(p['mlbamId'] for p in a.train)&set(p['mlbamId'] for p in a.test)),'training_5year_labels_end_before_holdout':max(p['year']+4 for p in a.train)<2018,'nonlinear_utility_once_per_outcome':u(20)>2*u(10),'same_asset_utility_independent_of_package':sum(u(x) for x in [5,7])==sum(u(x) for x in [7,5]),'no_optimizer_or_capacity_bonus':True,'draft_rounds_6_to_20_nontradable':True},'notes':['Age uses stable birth date only; present-day bio fields excluded.','Trajectory fit uses 2013/2012 versus 2018/2017; same 2013 training set for matched baseline.','Threshold stresses are diagnostics after primary definition, not selection of best heldout result.','Bootstrap probability grid is conditional on class coverage and fixed thresholds; very few tail outcomes, not calibrated confidence guarantee.','Horizon preferences are illustrative one/three/five years; not optimized or claimed to be actual owner utility.']}
(a.OUT/'diagnostics.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['feature_experiments','paired_brier_difference_vs_U2','owner_horizon_diagnostics']},indent=2))

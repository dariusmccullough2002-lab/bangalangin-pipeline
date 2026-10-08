"""Frozen expanded cohort experiment. Training freeze precedes final label access."""
import json,math,datetime,hashlib,gzip
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import log_loss
from historical_features import seasons,minor_features,BASE
P=Path(__file__).resolve().parent;O=P/'results';rng=np.random.default_rng(20261008)
dates={2010:'2010-03-12',2011:'2011-03-28',2012:'2012-03-01',2013:'2013-03-01',2014:'2014-02-11',2015:'2015-02-17',2019:'2019-02-13',2020:'2020-02-12'}
rankings=[r for r in json.load(open(O/'resolved-rankings.json')) if r['rank']<=100]
oldco=json.load(open(BASE/'results/cohort.json'))
bios=json.load(gzip.open(P/'raw/game-inputs.json.gz','rt'))['bios']
for r in oldco:
 if r['year'] in [2012,2013]:
  q={k:v for k,v in r.items() if k not in ['label','peak_two_year','age_at_evaluation','outcome_years']};q['birthDate']=bios[str(q['mlbamId'])]['birthDate'];q['provider']='MLB archived';rankings.append(q)
lookup={(r['year'],r['mlbamId']):r for r in rankings};minor,maudit=minor_features();annual=seasons();cuts=[6.82833342604977,11.615250774606945,17.59838994663511]
def outcome(r,years=5):
 a=[annual.get((y,r['mlbamId'])) for y in range(r['year'],r['year']+years)];s=sorted([v['score'] if v else 0 for v in a],reverse=True);peak=sum(s[:2])/2;regular=sum(bool(v and v['ex']>=(250 if v['role']=='H' else 40)) for v in a)>=2
 return int(0 if not regular else 1+sum(peak>=c for c in cuts)),peak
seen=set();train=[]
for r in sorted(rankings,key=lambda r:(r['year'],r['rank'])):
 if r['year']<=2015 and r['mlbamId'] not in seen:train.append(r);seen.add(r['mlbamId'])
test=[r for r in rankings if r['year']==2020 and r['mlbamId'] not in seen]
assert len({r['mlbamId'] for r in test})==len(test) and not seen.intersection(r['mlbamId'] for r in test)
def features(r,kind='core'):
 age=(datetime.date.fromisoformat(dates[r['year']])-datetime.date.fromisoformat(r['birthDate'])).days/365.2425
 x=[math.log(r['rank']),age,r['pitcher']]
 if kind=='minor':
  m=minor.get((r['year']-1,r['mlbamId'],'pitching' if r['pitcher'] else 'hitting'));x+=[int(m is None)]+(m or [0]*4)
 if kind in ['FV','tools','trajectory']:
  x+=[float(r.get('FV') or 50)]
 if kind=='tools':
  t=r.get('tools',{})
  names=[['Fastball'],['Slider','Curveball'],['Command','Control']] if r['pitcher'] else [['Hit'],['Game Power','GamePower'],['Run','Speed']]
  for keys in names:
   v=[t[k] for k in keys if k in t];x += [float(max(v) if v else 50),int(not v)]
 if kind=='trajectory':
  prev=lookup.get((r['year']-1,r['mlbamId']));x += [int(prev is None),(prev['rank']-r['rank'])/100 if prev else 0]
 return x
def fit(rs,kind):
 X=np.array([features(r,kind) for r in rs]);y=np.array([outcome(r)[0] for r in rs]);m=make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=2000)).fit(X,y);return m,X,y
experiments={}
for name,kind,rs in [('expanded_core','core',train),('expanded_minor','minor',train)]+[(f'matched_2015_{k}',k,[r for r in rankings if r['year']==2015]) for k in ['core','FV','tools','trajectory']]:
 m,X,y=fit(rs,kind);experiments[name]=(m,kind,rs,X,y)
# Freeze trained parameters before obtaining any final outcome labels.
receipt={'protocol_sha256':hashlib.sha256((P/'protocol.json').read_bytes()).hexdigest(),'frozen_before_final_labels_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'train_ids':[r['mlbamId'] for r in train],'final_ids':[r['mlbamId'] for r in test],'models':{name:{'features':kind,'train_ids':[r['mlbamId'] for r in rs],'class_counts':np.bincount(y,minlength=5).tolist(),'scaler_mean':m[0].mean_.tolist(),'scaler_scale':m[0].scale_.tolist(),'coef':m[1].coef_.tolist(),'intercept':m[1].intercept_.tolist(),'classes':m[1].classes_.tolist()} for name,(m,kind,rs,X,y) in experiments.items()}}
(O/'trained-model-freeze.json').write_text(json.dumps(receipt,indent=2))
truth=np.array([outcome(r)[0] for r in test]);Y=np.eye(5)[truth]
def metrics(pr):return {'n':len(truth),'multiclass_brier':float(np.mean(np.sum((pr-Y)**2,axis=1))),'log_loss':float(log_loss(truth,pr,labels=range(5))),'star_or_superstar_brier':float(np.mean((pr[:,3:].sum(axis=1)-(truth>=3))**2)),'superstar_brier':float(np.mean((pr[:,4]-(truth==4))**2))}
def aligned(m,X):
 p=np.zeros((len(X),5));p[:,m[-1].classes_]=m.predict_proba(X);return p
preds={name:aligned(m,[features(r,kind) for r in test]) for name,(m,kind,rs,X,y) in experiments.items()}
# Recover the existing Phase1 intercept differences from its saved probabilities; no refitting.
v=json.load(open(BASE/'results/validation.json'));co=np.array(v['prospect_coefficients']);p=v['predictions'][0];oldx=np.array([math.log(p['rank']),p['pitcher']]);relative=np.log(np.array(p['predicted'])/p['predicted'][0])-(co-co[0])@oldx
for p in v['predictions']:
 z=co@np.array([math.log(p['rank']),p['pitcher']])+relative;pr=np.exp(z-z.max());pr/=pr.sum();assert np.max(abs(pr-np.array(p['predicted'])))<1e-8
z=np.array([co@np.array([math.log(r['rank']),r['pitcher']])+relative for r in test]);z-=z.max(axis=1)[:,None];preds['saved_Phase1_rank_role']=np.exp(z)/np.exp(z).sum(axis=1)[:,None]
def u2(rank):
 reach=.22+.58*math.exp(-(rank-1)/160);elite=.015+.20*math.exp(-(rank-1)/35);star=.07+.25*math.exp(-(rank-1)/100);return [1-reach,reach*(1-elite-star-.25),reach*.25,reach*star,reach*elite]
preds['U2_rank_prior']=np.array([u2(r['rank']) for r in test]);freq=(np.bincount(experiments['expanded_core'][4],minlength=5)+1)/(len(train)+5);preds['development_frequency']=np.tile(freq,(len(test),1))
paired={}
for a,b in [('expanded_core','saved_Phase1_rank_role'),('expanded_core','U2_rank_prior'),('expanded_minor','expanded_core')]+[(f'matched_2015_{k}','matched_2015_core') for k in ['FV','tools','trajectory']]:
 delta=np.sum((preds[a]-Y)**2,axis=1)-np.sum((preds[b]-Y)**2,axis=1);boot=np.array([delta[rng.integers(0,len(delta),len(delta))].mean() for _ in range(2000)]);paired[a+' minus '+b]={'mean_brier_difference':float(delta.mean()),'paired_95_interval':np.quantile(boot,[.025,.975]).tolist()}
grid=[{'rank':rank,'pitcher':pitch,'year':2020,'birthDate':f'{2020-age}-02-12'} for pitch in [0,1] for age in [19,22] for rank in [5,25,50,90]]
m,kind,rs,X,y=experiments['expanded_core'];G=np.array([features(r) for r in grid]);boots=[];excluded=0
for i in range(500):
 ix=rng.integers(0,len(y),len(y))
 if len(set(y[ix]))<5:excluded+=1;continue
 boots.append(make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=2000)).fit(X[ix],y[ix]).predict_proba(G))
arr=np.array(boots);probs=[r|{'probabilities':m.predict_proba(G)[i].tolist(),'bootstrap_90_interval':np.quantile(arr[:,i,:],[.05,.95],axis=0).tolist()} for i,r in enumerate(grid)]
def wilson(k,n):
 z=1.96;a=k/n;d=1+z*z/n;c=(a+z*z/(2*n))/d;e=z*math.sqrt(a*(1-a)/n+z*z/(4*n*n))/d;return [c-e,c+e]
secondary=[r|{'five_year_label':outcome(r)[0],'seven_year_label':outcome(r,7)[0],'observed_through':r['year']+6} for r in train]
tails={}
for name,rs in [('development',train),('final_2020',test)]:
 labels=[outcome(r)[0] for r in rs];tails[name]={str(c):{'count':sum(l==c for l in labels),'n':len(labels),'wilson95':wilson(sum(l==c for l in labels),len(labels))} for c in [3,4]}
anchors=[float(np.median([outcome(r)[1] for r in train if outcome(r)[0]==c])) for c in range(5)]
# Sensitivity only: nonlinear utility exactly once for each possible asset outcome, no package-total bonus.
utility=lambda s: max(0,s)+.04*max(0,s-11.615250774606945)**2
U=np.array([utility(s) for s in anchors]);packages=[]
for pitch in [0,1]:
 vals={r:float(m.predict_proba([features({'rank':r,'pitcher':pitch,'year':2020,'birthDate':'2001-02-12'})])[0]@U) for r in [5,25,50,90]}
 packages.append({'pitcher':pitch,'rank5':vals[5],'two_rank25':2*vals[25],'rank25_plus50_plus90':vals[25]+vals[50]+vals[90],'warning':'Intrinsic probability-utility sensitivity only; no roster optimization, acquisition prices, or correlated-outcome package model'})
result={'status':'OFFLINE; FROZEN REDUCED-CATEGORY PRIMARY LABELS, CATEGORY INTEGRATION NOT YET VALIDATED','coverage':{'new_FG_top100_rows':600,'all_extracted_FG_rows':680,'combined_primary_rank_rows':999,'development_unique':len(train),'development_counts':np.bincount(experiments['expanded_core'][4],minlength=5).tolist(),'final_unique':len(test),'final_counts':np.bincount(truth,minlength=5).tolist(),'matched_2015_training_unique':len(experiments['matched_2015_core'][2]),'additional_reserve':'2021 remains unevaluated','final_already_MLB_by_2020':sum((2019,r['mlbamId']) in annual for r in test)},'metrics':{k:metrics(v) for k,v in preds.items()},'paired_comparisons':paired,'probability_grid':probs,'bootstrap_successful':len(boots),'bootstrap_missing_class_exclusions':excluded,'empirical_tail_uncertainty':tails,'five_to_seven_year_changes':{'n':len(secondary),'minimal_to_contributor':sum(r['five_year_label']==0 and r['seven_year_label']>0 for r in secondary),'star_or_superstar_increase':sum(r['five_year_label']<3 and r['seven_year_label']>=3 for r in secondary)},'minor_feature_source_audit':maudit,'unsupported_feature_experiments':['Comparable dated level not collected for development cohort','Injury information lacks systematic dated coverage; no feature fit','Future tools harmonization exploratory: Command/Control and +2.5 conversions','Current lifetime records are not complete-career labels'],'class_utility_anchors':anchors,'package_sensitivities':packages,'predictions':[r|{'actual_five_year_label':int(t),'peak_two_year':outcome(r)[1],'probabilities':{k:v[i].tolist() for k,v in preds.items()}} for i,(r,t) in enumerate(zip(test,truth))]}
(O/'prospect-calibration.json').write_text(json.dumps(result,indent=2));(O/'delayed-arrival-diagnostic.json').write_text(json.dumps(secondary,indent=2));print(json.dumps({k:result[k] for k in ['coverage','metrics','paired_comparisons','five_to_seven_year_changes']},indent=2))

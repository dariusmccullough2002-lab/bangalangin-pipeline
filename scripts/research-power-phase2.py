"""Reproducible exploratory sensitivity audit; never writes ranking/model V1 inputs.
2024–2026 were already inspected in Phase 1. These are reused temporal tests,
not a new untouched confirmation sample. No candidate is automatically promoted.
"""
from pathlib import Path
import json, hashlib, warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, SplineTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss, confusion_matrix
warnings.filterwarnings('ignore', category=UserWarning)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research/phase2';OUT.mkdir(exist_ok=True)
source=ROOT/'data/research/power-translation-source.csv'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='863efa0edae9cafa83104b5ee5c7fe2d8eb51469b1a3112d3e708d203d70173f'
d=pd.read_csv(source).rename(columns={'oz_swing_percent':'chase','whiff_percent':'whiff','hard_hit_percent':'hard_hit','barrel_batted_rate':'barrel','isolated_power':'iso'})
d['qualified']=np.where(d.year.eq(2020),d.pa.ge(186),d.pa.ge(502))
F=['chase','whiff','hard_hit','barrel']
def lr():return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,random_state=20))
def models():
 return {
 'Hard-Hit':(['hard_hit'],lr()),'Barrel':(['barrel'],lr()),
 'Chase + Whiff':(F[:2],lr()),'Hard-Hit + Barrel':(F[2:],lr()),
 'Four components':(F,lr()),
 'Pairwise interactions':(F,make_pipeline(StandardScaler(),PolynomialFeatures(2,interaction_only=True,include_bias=False),StandardScaler(),LogisticRegression(C=1,max_iter=2000))),
 'Quadratic':(F,make_pipeline(StandardScaler(),PolynomialFeatures(2,include_bias=False),StandardScaler(),LogisticRegression(C=1,max_iter=2000))),
 'Spline additive':(F,make_pipeline(SplineTransformer(n_knots=4,degree=3),StandardScaler(),LogisticRegression(C=1,max_iter=2000))),
 'Decision tree':(F,DecisionTreeClassifier(max_depth=3,min_samples_leaf=40,random_state=20)),
 'Random forest':(F,RandomForestClassifier(n_estimators=80,max_depth=5,min_samples_leaf=20,n_jobs=2,random_state=20)),
 'Gradient boosting':(F,HistGradientBoostingClassifier(max_iter=80,max_leaf_nodes=7,min_samples_leaf=30,l2_regularization=5,random_state=20)),
 'Zone / discipline extension':(F+['z_swing_percent','z_swing_miss_percent','swing_percent','k_percent','bb_percent'],lr()),
 'ISO (same-season target overlap)':(['iso'],lr()),
 'wOBA (same-season target overlap)':(['woba'],lr()),
 'xSLG (same-season outcome proxy)':(['xslg'],lr())}
def metrics(y,p):
 tn,fp,fn,tp=confusion_matrix(y,p>=.5,labels=[0,1]).ravel();n=len(y)
 top=np.argsort(-p,kind='stable')[:max(1,int(np.ceil(n/10)))];base=float(np.mean(y))
 return dict(n=n,events=int(sum(y)),auc=float(roc_auc_score(y,p)),brier=float(brier_score_loss(y,p)),logLoss=float(log_loss(y,p)),precision=float(tp/(tp+fp)) if tp+fp else None,recall=float(tp/(tp+fn)) if tp+fn else None,falsePositiveRate=float(fp/(fp+tn)) if fp+tn else None,falseNegativeRate=float(fn/(fn+tp)) if fn+tp else None,topDecileLift=float(np.mean(np.asarray(y)[top])/base) if base else None)
def buckets(y,p):
 return [dict(low=i/10,high=(i+1)/10,n=int(k.sum()),predicted=float(p[k].mean()) if k.any() else None,observed=float(np.asarray(y)[k].mean()) if k.any() else None) for i in range(10) for k in [(p>=i/10)&((p<(i+1)/10) if i<9 else (p<=1))]]
results=[];calibration=[]
endpoints={f'ISO ≥ {iso:.3f} & wOBA ≥ {w:.3f}':(d.iso.ge(iso)&d.woba.ge(w)).astype(int) for iso in [.18,.20,.22] for w in [.32,.33,.34]}
endpoints.update({f'xSLG ≥ {v:.3f}':d.xslg.ge(v).astype(int) for v in [.42,.45,.48]})
samples={f'{n}+ PA':d.pa.ge(n) for n in [150,200,300,400]};samples['Qualified']=d.qualified
for sample,mask in samples.items():
 for endpoint,y in endpoints.items():
  sub=d[mask].copy();sub['target']=y[mask];tr=sub[sub.year<=2023];te=sub[sub.year>=2024]
  if min(tr.target.value_counts().min(),te.target.value_counts().min())<10:continue
  for name,(cols,model) in models().items():
   model.fit(tr[cols],tr.target);p=model.predict_proba(te[cols])[:,1]
   r=dict(sample=sample,endpoint=endpoint,model=name,trainN=len(tr),**metrics(te.target,p));results.append(r)
   if sample=='Qualified' and endpoint=='ISO ≥ 0.200 & wOBA ≥ 0.330':calibration.append(dict(model=name,buckets=buckets(te.target,p)))
 print('completed',sample,flush=True)
pd.DataFrame(results).to_csv(OUT/'sensitivity.csv',index=False)
# Rolling origins: parameters are fixed in advance and no test-year tuning is used.
rolling=[]
for test_year in range(2020,2027):
 tr=d[d.qualified & d.year.lt(test_year)].copy();te=d[d.qualified & d.year.eq(test_year)].copy()
 ytr=(tr.iso.ge(.2)&tr.woba.ge(.33)).astype(int);yte=(te.iso.ge(.2)&te.woba.ge(.33)).astype(int)
 for name,(cols,model) in models().items():
  if 'same-season' in name:continue
  model.fit(tr[cols],ytr);p=model.predict_proba(te[cols])[:,1]
  rolling.append(dict(year=test_year,model=name,trainN=len(tr),**metrics(yte,p)))
pd.DataFrame(rolling).to_csv(OUT/'rolling.csv',index=False)
# Retained consecutive-season forecasts: features only at t, target only at t+1.
future=d[['player_id','year','iso','woba','pa']].copy();future.year-=1;future=future.rename(columns={'iso':'nextIso','woba':'nextWoba','pa':'nextPA'})
pairs=d.merge(future,on=['player_id','year'],validate='one_to_one');pairs=pairs[pairs.qualified & pairs.nextPA.ge(200)].copy();pairs['target']=(pairs.nextIso.ge(.2)&pairs.nextWoba.ge(.33)).astype(int)
future_results=[]
# Keep target years chronological: development targets <=2023, tests 2024–2026.
tr=pairs[pairs.year<=2022];te=pairs[pairs.year.between(2023,2025)]
for name,(cols,model) in {**{k:v for k,v in models().items() if 'same-season' not in k},'Prior ISO':(['iso'],lr()),'Prior wOBA':(['woba'],lr()),'Prior ISO + wOBA':(['iso','woba'],lr()),'Prior ISO + wOBA + K + BB':(['iso','woba','k_percent','bb_percent'],lr())}.items():
 model.fit(tr[cols],tr.target);p=model.predict_proba(te[cols])[:,1];future_results.append(dict(model=name,trainN=len(tr),**metrics(te.target,p)))
pd.DataFrame(future_results).to_csv(OUT/'next-year.csv',index=False)
# Two consecutive successful seasons; missing opportunities are censored, never failures.
sustained=[]
pairs['nowSuccess']=pairs.iso.ge(.2)&pairs.woba.ge(.33);pairs['both']=pairs.nowSuccess & pairs.target.eq(1)
for name,(cols,model) in {k:v for k,v in models().items() if k in ['Hard-Hit','Barrel','Hard-Hit + Barrel','Four components','Quadratic','Spline additive']}.items():
 tr=pairs[pairs.year<=2022];te=pairs[pairs.year.between(2023,2025)];model.fit(tr[cols],tr.both);p=model.predict_proba(te[cols])[:,1];sustained.append(dict(model=name,trainN=len(tr),**metrics(te.both,p)))
def region_stats(g):
 n=len(g);e=int((g.iso.ge(.2)&g.woba.ge(.33)).sum());rate=e/n if n else None
 if n:
  z=1.96;center=(rate+z*z/(2*n))/(1+z*z/n);half=z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/(1+z*z/n)
 else:center=half=None
 return dict(n=n,events=e,successRate=rate,wilsonLow=center-half if n else None,wilsonHigh=center+half if n else None,status='sparse / exploratory' if n<25 else 'descriptive',**{f'median_{c}':float(g[c].median()) if n else None for c in ['hard_hit','barrel','iso','woba']},isoP10=float(g.iso.quantile(.1)) if n else None,isoP90=float(g.iso.quantile(.9)) if n else None)
regions=[];impact=[];archetypes=[];q=d[d.qualified]
for period,frame in [('Development ≤2023',q[q.year<=2023]),('Reused temporal test 2024–2026',q[q.year>=2024])]:
 for cl,ch in zip([-np.inf,25,30,32,35,38],[25,30,32,35,38,np.inf]):
  for wl,wh in zip([-np.inf,20,25,28,30,33,36],[20,25,28,30,33,36,np.inf]):
   g=frame[frame.chase.ge(cl)&frame.chase.lt(ch)&frame.whiff.ge(wl)&frame.whiff.lt(wh)];regions.append(dict(period=period,chaseBand=f'{cl} to {ch}',whiffBand=f'{wl} to {wh}',**region_stats(g)))
 for chase,whiff in [(35,30),(38,33)]:
  high=frame[frame.chase.ge(chase)&frame.whiff.ge(whiff)]
  for metric,edges in [('hard_hit',[-np.inf,35,40,45,50,55,np.inf]),('barrel',[-np.inf,5,8,10,12,15,np.inf])]:
   for low,hi in zip(edges,edges[1:]):impact.append(dict(period=period,minChase=chase,minWhiff=whiff,metric=metric,band=f'{low} to {hi}',**region_stats(high[high[metric].ge(low)&high[metric].lt(hi)])))
 for chase in [False,True]:
  for whiff in [False,True]:archetypes.append(dict(period=period,profile=f'{"High" if chase else "Low"} Chase / {"High" if whiff else "Low"} Whiff',**region_stats(frame[frame.chase.ge(35).eq(chase)&frame.whiff.ge(30).eq(whiff)])))
 for zone in [False,True]:archetypes.append(dict(period=period,profile=f'Low Chase / {"High" if zone else "Low"} Zone Swing (65% illustrative split)',**region_stats(frame[frame.chase.lt(35)&frame.z_swing_percent.ge(65).eq(zone)])))
for name,records in [('regions',regions),('impact',impact),('archetypes',archetypes),('sustained',sustained)]:pd.DataFrame(records).to_csv(OUT/f'{name}.csv',index=False)
baseline=[r for r in results if r['sample']=='Qualified' and r['endpoint']=='ISO ≥ 0.200 & wOBA ≥ 0.330']
summary=dict(asOf='2026-11-20',status='Experimental; no model promotion',sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),design='Fixed candidate specifications; fit through 2023 and evaluate 2024–2026. Reused Phase 1 test years; exploratory multiple comparisons, not independent confirmation.',candidateTests=len(results),primary=baseline,calibration=calibration,rolling=rolling,nextYear=future_results,sustained=sustained,archetypes=archetypes,impact=impact,limitations=['Player-seasons are repeated observations; intervals below are descriptive binomial intervals, not player-cluster inference.','Same-season ISO and wOBA overlap the endpoint and are diagnostic ceilings, ineligible for model promotion. xSLG is an outcome proxy.','Qualified selection excludes players who lost playing time. Forecasts condition on next-year 200+ PA; attrition is not scored as failure.','No independent post-2026 temporal confirmation; no selection of a new winning model from reused test results.','HR 20/25/30 and OPS endpoints unavailable in the frozen 19-column source. wRC+ unavailable. EV90, maxEV, Pull-Air and raw launch-angle panel absent.','Additive spline logistic is a GAM-like model, not a separately tuned GAM. Three-way interactions deferred until stronger evidence and clustered validation.','MiLB-to-MLB developmental outcomes, age/level/park adjustments and historical maturation paths are not validated.','No universal frontier is established. No current rankings, grades, trade values, recommendations or Decision Lab inputs change.'])
(OUT/'summary.json').write_text(json.dumps(summary,separators=(',',':'),allow_nan=False))
print(json.dumps(dict(candidateTests=len(results),primary=[{k:r[k] for k in ['model','auc','brier']} for r in baseline])),flush=True)

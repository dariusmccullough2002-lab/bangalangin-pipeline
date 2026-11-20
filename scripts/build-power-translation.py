"""Export the existing V1 MLB model and data. No ranking inputs are written.
Run with the research runtime (numpy/pandas/scipy/scikit-learn installed).
Input: official, unchanged Savant CSV; validated source SHA below.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,roc_auc_score
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/research/power-translation-source.csv'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='863efa0edae9cafa83104b5ee5c7fe2d8eb51469b1a3112d3e708d203d70173f'
d=pd.read_csv(source).rename(columns={'last_name, first_name':'name','oz_swing_percent':'chase','whiff_percent':'whiff','hard_hit_percent':'hard_hit','barrel_batted_rate':'barrel','isolated_power':'iso'})
d['qualified']=np.where(d.year.eq(2020),d.pa.ge(186),d.pa.ge(502))
d['endpoint']=(d.iso.ge(.200)&d.woba.ge(.330)).astype(int)
features=['chase','whiff','hard_hit','barrel'];q=d[d.qualified];train=q[q.year<=2021];val=q[q.year.between(2022,2023)];dev=q[q.year<=2023];test=q[q.year>=2024]
best=(float('inf'),None)
for c in [.1,1,10]:
 m=make_pipeline(StandardScaler(),LogisticRegression(C=c,max_iter=3000,random_state=20261120));m.fit(train[features],train.endpoint)
 loss=log_loss(val.endpoint,m.predict_proba(val[features])[:,1])
 if loss<best[0]:best=(loss,c)
m=make_pipeline(StandardScaler(),LogisticRegression(C=best[1],max_iter=3000,random_state=20261120));m.fit(dev[features],dev.endpoint)
auc=roc_auc_score(test.endpoint,m.predict_proba(test[features])[:,1]);assert abs(auc-.9136807817589576)<1e-10
mu=m[0].mean_;sd=m[0].scale_;coef=m[-1].coef_[0]/sd;intercept=float(m[-1].intercept_[0]-np.sum(coef*mu))
x=dev[features].to_numpy();hull=Delaunay((x-mu)/sd)
def support(points):
 inside=hull.find_simplex((points-mu)/sd)>=0
 counts=np.array([np.all(np.abs(x-p)<=np.array([5,5,5,3]),axis=1).sum() for p in points])
 return inside&(counts>=25),counts
valid,n=support(d[features].to_numpy());d['supported']=valid;d['nearby_n']=n
rows=[]
for _,p in d.iterrows():
 last,first=p['name'].split(', ',1)
 rows.append({'id':f'{int(p.player_id)}-{int(p.year)}','playerId':int(p.player_id),'name':f'{first} {last}','year':int(p.year),'pa':int(p.pa),**{f:float(p[f]) for f in features+['iso','woba','xslg']},'qualified':bool(p.qualified),'endpoint':bool(p.endpoint),'supported':bool(p.supported),'nearbyN':int(p.nearby_n)})
# Conditional risk slice: equal Chase and Whiff z-scores; Barrel stays fixed.
# This is not the actual probability of every point sharing the projected risk.
risks=np.round(np.arange(-2,2.501,.1),2);hh=np.arange(20,66,1)
slices=[]
for barrel in range(0,26):
 pts=np.array([[mu[0]+r*sd[0],mu[1]+r*sd[1],float(h),float(barrel)] for h in hh for r in risks]);ok,counts=support(pts)
 probs=m.predict_proba(pd.DataFrame(pts,columns=features))[:,1]
 slices.append([round(float(p),4) if yes else None for p,yes in zip(probs,ok)])
model={'features':features,'means':mu.tolist(),'scales':sd.tolist(),'coefficients':coef.tolist(),'intercept':intercept,'C':best[1],'trainThrough':2023,'holdoutYears':[2024,2025,2026],'holdoutN':len(test),'holdoutEvents':int(test.endpoint.sum()),'auc':auc,'defaultBarrel':int(round(dev.barrel.median())),'riskGrid':risks.tolist(),'hardHitGrid':hh.tolist(),'slices':slices,'supportRule':'Within the four-metric development convex hull and at least 25 training seasons within ±5pp Chase/Whiff/Hard-Hit and ±3pp Barrel. Exploratory display guard, not validated uncertainty.'}
manifest={'version':'Research preview V1 / 2026-11-20','source':'Baseball Savant official custom leaderboard CSV','sourceUrl':'https://baseballsavant.mlb.com/leaderboard/custom','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'retrieved':'2026-11-20','rows':len(d),'qualifiedRows':len(q),'developmentRows':len(dev),'scope':'MLB, 2015–2026, 100+ PA. Model trained on qualified-PA proxy only (502 PA; 186 in 2020).','endpoint':'ISO ≥ .200 AND wOBA ≥ .330','limitations':['wRC+ unavailable; raw wOBA is not park/league adjusted','Not a causal model or a future MLB-success probability','No validated MiLB translation','2026 data reflect source snapshot; no automatic refresh','50% conditional frontier is a visualization convention, not a prospect threshold']}
(ROOT/'data/research/power-translation-v1.json').write_text(json.dumps({'manifest':manifest,'model':model,'seasons':rows},separators=(',',':'),allow_nan=False))
print(json.dumps({'rows':len(rows),'qualified':len(q),'development':len(dev),'holdout':len(test),'auc':auc,'C':best[1],'supported':int(valid.sum())}))
# Coverage audit stays separate from the model. No prose-derived measurements.
universe=ROOT/'data/editions/october-2026.json'
if not universe.exists():universe=ROOT/'universe.json' # isolated review checkout only
u=json.loads(universe.read_text());players=[]
for p in u['rankings']:
 if p.get('type')=='P' or p.get('position') in ['P','SP','RP','RHP','LHP']:continue
 players.append({k:p.get(k) for k in ['name','playerId','mlbamId','age','level','mlbOrg','organization']})
coverage={'asOf':'2026-11-20','universe':'Non-debuted position players in the November 2026 BangaLangin league board; not every minor leaguer.','metadataAsOf':u['asOf'],'ownershipSnapshot':u['ownershipSnapshotId'],'required':['Chase%','Whiff%','Hard-Hit%','Barrel%'],'eligible':0,'reason':'No source-reviewed, same-season/same-level four-metric MiLB panel has been ingested into this research release. This is a coverage gap in this lab, not a claim that no tracking data exists.','players':players}
(ROOT/'data/research/power-translation-coverage.json').write_text(json.dumps(coverage,separators=(',',':')))

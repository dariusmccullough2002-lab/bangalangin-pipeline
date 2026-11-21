"""Paired player-cluster bootstrap of the reused temporal test.
Fixed predictions, not model refits; no ranking inputs or displayed coefficients change.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
ROOT=Path(__file__).resolve().parents[1]
d=pd.read_csv(ROOT/'data/research/power-translation-source.csv').rename(columns={'oz_swing_percent':'chase','whiff_percent':'whiff','hard_hit_percent':'hard_hit','barrel_batted_rate':'barrel','isolated_power':'iso'})
d=d[np.where(d.year.eq(2020),d.pa.ge(186),d.pa.ge(502))].copy()
d['y']=(d.iso.ge(.2)&d.woba.ge(.33)).astype(int)
train=d[d.year<=2021];val=d[d.year.between(2022,2023)];dev=d[d.year<=2023];test=d[d.year>=2024].reset_index(drop=True)
model=json.loads((ROOT/'data/research/power-translation-v1.json').read_text())['model']
features=model['features'];x=test[features].to_numpy();logit=model['intercept']+x@np.array(model['coefficients']);four=1/(1+np.exp(-logit))
candidates=[]
for c in [.1,1,10]:
 p=make_pipeline(StandardScaler(),LogisticRegression(C=c,max_iter=3000,random_state=20261120)).fit(train[['barrel']],train.y)
 candidates.append((log_loss(val.y,p.predict_proba(val[['barrel']])[:,1]),c))
best=min(candidates)[1]
barrel_model=make_pipeline(StandardScaler(),LogisticRegression(C=best,max_iter=3000,random_state=20261120)).fit(dev[['barrel']],dev.y)
barrel=barrel_model.predict_proba(test[['barrel']])[:,1]
ids=test.player_id.unique();groups={pid:np.flatnonzero(test.player_id.to_numpy()==pid) for pid in ids};rng=np.random.default_rng(20261120);deltas=[]
for _ in range(1000):
 idx=np.concatenate([groups[i] for i in rng.choice(ids,len(ids),replace=True)]);y=test.y.iloc[idx]
 if y.nunique()<2:continue
 deltas.append((roc_auc_score(y,four[idx])-roc_auc_score(y,barrel[idx]),brier_score_loss(y,four[idx])-brier_score_loss(y,barrel[idx])))
v=np.array(deltas)
result=dict(asOf='2026-11-20',status='Exploratory; no model promotion',n=len(test),uniquePlayers=len(ids),replicates=len(v),design='Paired player-cluster percentile bootstrap with fixed fitted predictions; all seasons for a sampled player move together. Reused 2024–2026 temporal test, not independent confirmation. This interval omits training/refit uncertainty.',fourAuc=float(roc_auc_score(test.y,four)),barrelAuc=float(roc_auc_score(test.y,barrel)),barrelC=best,aucDifference=float(roc_auc_score(test.y,four)-roc_auc_score(test.y,barrel)),aucDifference95=np.quantile(v[:,0],[.025,.975]).tolist(),brierDifference=float(brier_score_loss(test.y,four)-brier_score_loss(test.y,barrel)),brierDifference95=np.quantile(v[:,1],[.025,.975]).tolist(),interpretation='AUC delta above zero favors four components; Brier delta below zero favors four components. No interval here validates raw MiLB translation, a universal frontier, or next-year improvement.')
(ROOT/'data/research/phase2/reference-uncertainty.json').write_text(json.dumps(result,separators=(',',':')))
print(json.dumps(result,indent=2))

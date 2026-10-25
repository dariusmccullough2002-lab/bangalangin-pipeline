"""Offline scale/coverage audit. Fixed five-fold ID split; no player-specific prices or production writes."""
import gzip,json,csv,hashlib,math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.isotonic import IsotonicRegression
R=Path('docs/valuation-priorities-20261024');d=json.loads(gzip.decompress((R/'Frozen_Inputs.json.gz').read_bytes()));A=d['assets']
P=[a for a in A if a['audit']['kind']!='pick'];pairs=[a for a in P if a.get('ranking_policy') and a['audit']['kind']!='prospect']
x=np.array([a['ranking_policy']['contribution_value'] for a in pairs]);y=np.array([a['values']['neutral']['display'] for a in pairs]);ratio=y/np.maximum(x,1e-9)
# Original audit compared archived neutral contributions. Also report current shared-quality-adjusted diagnostics separately.
current=np.array([a['competitive_values']['balanced']['display'] for a in pairs]);fold=np.array([int(hashlib.sha256(a['id'].encode()).hexdigest()[:8],16)%5 for a in pairs]);pred={k:np.zeros(len(x)) for k in ['identity','single-factor','monotone']}
for k in range(5):
 train=fold!=k;test=~train
 pred['identity'][test]=x[test]
 factor=np.median(y[train & (x>0)]/x[train & (x>0)])
 pred['single-factor'][test]=x[test]*factor
 fit=IsotonicRegression(out_of_bounds='clip').fit(np.log1p(x[train]),np.log1p(y[train]))
 pred['monotone'][test]=np.expm1(fit.predict(np.log1p(x[test])))
def metrics(p,t):
 log=np.abs(np.log1p(p)-np.log1p(t));rel=np.abs(p-t)/np.maximum(t,1e-9)
 return dict(n=len(t),medianAbsoluteLogError=float(np.median(log)),within25Percent=float(np.mean(rel<=.25)),medianAbsoluteError=float(np.median(np.abs(p-t))),spearman=float(spearmanr(p,t).statistic))
cv={k:metrics(p,y) for k,p in pred.items()};gates={k:{'within25Percent>=.80':m['within25Percent']>=.8,'spearman>=.80':m['spearman']>=.8,'medianLogError<=log(1.25)':m['medianAbsoluteLogError']<=math.log(1.25)} for k,m in cv.items()}
floor=min(a['values']['neutral']['display'] for a in P if a.get('ranking_policy'));above=[a for a in P if not a.get('ranking_policy') and a['values']['neutral']['display']>floor and a.get('owner') not in [None,'Free agent']]
sources={}
for scope,file in [('overall','overall.tsv'),('prospect','prospects.tsv')]:
 with open('docs/value-audit-20261012/inputs/'+file) as f: rows=list(csv.DictReader(f,delimiter='\t'))
 sources[scope]={r['Player ID'].strip('*'):r for r in rows}
missed=[a['id'] for a in P if not a.get('ranking_policy') and any(a['id'] in v for v in sources.values())]
quantiles=[]
for ids in np.array_split(np.argsort(x),4):quantiles.append(dict(n=len(ids),productionRange=[float(x[ids].min()),float(x[ids].max())],medianRatio=float(np.median(ratio[ids]))))
classes={}
for role in ['H','SP','RP','H+SP']:
 ids=np.array([a['audit']['role']==role for a in pairs]);
 if ids.sum():classes[role]={'count':int(ids.sum()),'candidateMetrics':{k:metrics(p[ids],y[ids]) for k,p in pred.items()}}
# Low production is censored by ranking-list membership, so a nonzero intercept must not be applied to every unranked player.
coverage=dict(players=len(P),rankingLed=sum(bool(a.get('ranking_policy')) for a in P),productionOnly=sum(not a.get('ranking_policy') for a in P),rankFloor=floor,ownedProductionOnlyAboveFloor=len(above),stableIdSourceMatchesWithoutPolicy=missed,sourceRows={k:len(v) for k,v in sources.items()},missingSourcePublicationDate=sum(a.get('ranking_policy',{}).get('source_publication_date')=='not independently established' for a in P))
result=dict(inputSha256=hashlib.sha256((R/'Frozen_Inputs.json.gz').read_bytes()).hexdigest(),coverage=coverage,archivedPaired=dict(n=len(x),p10=float(np.percentile(ratio,10)),median=float(np.median(ratio)),p90=float(np.percentile(ratio,90)),spearman=float(spearmanr(x,y).statistic)),currentPaired=metrics(current,y),byProductionQuartile=quantiles,crossValidation=cv,acceptanceGates=gates,byRole=classes,approvedRepricing=False,selectionLimit='Ranked overlap is selected/truncated; it does not validate extrapolation into unranked players or missing graduates.',aboveFloor=[dict(id=a['id'],name=a['name'],value=a['values']['neutral']['display'],overallSourcePresent=a['id'] in sources['overall'],prospectSourcePresent=a['id'] in sources['prospect']) for a in above])
(R/'Scale_Results.json').write_text(json.dumps(result,indent=2)+'\n')
with (R/'Scale_Heldout_Predictions.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['id','name','fold','production','neutral','currentProduction',*pred]);w.writerows([a['id'],a['name'],int(fold[i]),float(x[i]),float(y[i]),float(current[i]),*[float(p[i]) for p in pred.values()]] for i,a in enumerate(pairs))
print(json.dumps({k:result[k] for k in ['coverage','archivedPaired','crossValidation','acceptanceGates']},indent=2))

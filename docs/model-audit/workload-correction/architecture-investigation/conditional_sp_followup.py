"""Fixed exploratory follow-up; reuse cases, no production writes or source collection."""
import sys,json,gzip,copy,functools,hashlib
from pathlib import Path
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
OUT=Path(__file__).resolve().parent
main=OUT/'quality_aware.py';env={'__file__':str(main),'__name__':'conditional_helpers'}
exec(compile(main.read_text().split('cases=[];manifest=[]')[0],str(main),'exec'),env)
base=env['env'];records=env['records'];lookup=env['lookup'];settings=env['settings']
original_xrow=env['xrow'];cache={}
def xrow(z):
 key=(z['id'],z['year'],z['role'])
 if key not in cache:cache[key]=original_xrow(z)
 return cache[key]
env['xrow']=xrow
METHODS=['future_role_caps','linear_SP','pooled_linear_SP']
saved=json.loads(gzip.decompress((OUT/'Quality_Aware_Cases.json.gz').read_bytes()))
by={(z['mlbam_id'],z['anchor'],z['role']):z for z in saved}
def label(z):
 return 0 if z['target']==0 else 2 if lookup.get((z['id'],z['year']+1,'P'),{}).get('role')=='SP' else 1
def train(rr,year,development=False):return base['training'](rr,year,development)
def fit(rows,pooled):
 model=env['fit'](rows)
 def linear(xs):
  xs=[z for z in xs if label(z)==2]
  return make_pipeline(StandardScaler(),Ridge(alpha=100)).fit(np.stack([xrow(z) for z in xs]),np.array([z['target'] for z in xs]))
 return model,linear(rows),linear(pooled)
def predict(models,rows,year):
 (classifier,regs,_),linear,pooled=models
 X=np.stack([xrow(z) for z in rows]);probs=classifier.predict_proba(X);preds={m:np.zeros(len(rows)) for m in METHODS}
 for col,l in enumerate(classifier.classes_):
  if l not in regs:continue
  cap=base['cap_at']('SP' if l==2 else 'RP',year)
  tree=np.clip(regs[l].predict(X),0,cap)
  for m in METHODS:
   cond=np.clip((linear if m=='linear_SP' else pooled).predict(X),0,cap) if l==2 and m!='future_role_caps' else tree
   preds[m]+=probs[:,col]*cond
 return preds
dev={m:[] for m in METHODS};manifest=[]
for year in [2016,2017,2018,2021,2022]:
 pooled=train('SP',year,True)+train('RP',year,True)
 for rr in ['SP','RP']:
  rows=train(rr,year,True);xs=[z for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  if not xs:continue
  preds=predict(fit(rows,pooled),xs,year)
  for m in METHODS:dev[m].extend((float(a),z['target'],rr) for a,z in zip(preds[m],xs))
def metrics(pairs):
 errors=np.asarray([a-b for a,b in pairs]);return {'n':len(errors),'MAE':float(np.mean(abs(errors))),'bias':float(np.mean(errors)),'RMSE':float(np.sqrt(np.mean(errors**2)))}
# Equal role weighting prevents the more numerous RP cases alone choosing the candidate.
devscores={m:{rr:metrics([(a,b) for a,b,r in xs if r==rr]) for rr in ['SP','RP']} for m,xs in dev.items()}
objective={m:sum((devscores[m][r]['MAE']+.25*abs(devscores[m][r]['bias']))/(150 if r=='SP' else 50) for r in ['SP','RP']) for m in METHODS}
chosen=min(METHODS,key=lambda m:objective[m]);print('Development selected',chosen,objective,flush=True)
cases=[]
for year in base['ANCHORS']:
 pooled=train('SP',year)+train('RP',year)
 for rr in ['SP','RP']:
  rows=train(rr,year);xs=[z for z in records[rr] if (z['id'],year,rr) in by and z['year']==year]
  if not xs:continue
  preds=predict(fit(rows,pooled),xs,year)
  manifest.append({'anchor':year,'role':rr,'latest_target':max(z['year']+1 for z in pooled),'id_mods':sorted({z['id']%5 for z in pooled})})
  for i,z in enumerate(xs):
   q=copy.deepcopy(by[z['id'],year,rr])
   for method in METHODS:
    factor=float(preds[method][i])/q['baseline']['IP'];q[method]={k:v*factor for k,v in q['baseline'].items()}
    for k in ['SV','HLD']:q[method][k]=q['baseline'].get(k,0)*min(1,factor)
   q['followup_selected']=q[chosen];cases.append(q)
 print('Completed',year,flush=True)
def scores(xs):
 result={}
 groups=sorted({g for z in xs for g in z['groups']})
 for group in groups:
  rows=[z for z in xs if group in z['groups']]
  result[group]={'n':len(rows),'metrics':{k:{m:metrics([(z[m].get(k,0),z['actual'].get(k,0)) for z in rows]) for m in ['baseline','selected','role_aware',*METHODS,'followup_selected']} for k in ['IP','K','QA3']}}
 return result
old=json.loads((OUT.parent/'Historical_Cases.json').read_text());index={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
for z in old:
 q=copy.deepcopy(index[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
 for method in ['selected','role_aware',*METHODS,'followup_selected']:
  factor=q[method]['IP']/z['baseline']['IP'];q[method]={k:v*factor for k,v in z['baseline'].items()}
  for k in ['SV','HLD']:q[method][k]=z['baseline'].get(k,0)*min(1,factor)
 frozen.append(q)
assert len(cases)==1084 and len(frozen)==94
assert all(z['latest_target']<=z['anchor'] and 0 not in z['id_mods'] for z in manifest)
result={'selected_by_development':chosen,'development':devscores,'objective':objective,'manifest':manifest,'expanded':scores(cases),'frozen94':scores(frozen),'scope':'Exploratory exposed historical cohorts; future role only defines training labels and scoring groups. No names, manual boosts, collection, or deployment.'}
(OUT/'Conditional_SP_Validation.json').write_text(json.dumps(result,indent=2))
(OUT/'Conditional_SP_Cases.json.gz').write_bytes(gzip.compress(json.dumps(cases).encode(),mtime=0))
for group in ['all','SP','RP','next_role_SP','first_MLB_season','second_MLB_season']:
 print(group,result['expanded'][group]['metrics']['IP'],flush=True)

# General current sensitivities; first-year only, no mutation of baseline inputs.
current=json.loads(gzip.decompress((OUT/'Quality_Aware_Current_Impact.json.gz').read_bytes()))
pooled=train('SP',2026)+train('RP',2026)
models={rr:fit(train(rr,2026),pooled) for rr in ['SP','RP']}
impact=[]
for rr in ['SP','RP']:
 xs=[];source=[]
 for z in current:
  if z['role']!=rr:continue
  p=base['old'].players[z['id']];ident=base['v'].cf.IDS.get(z['id'],p.get('mlbamId'));rows=base['v'].seasons(p,rr)
  f=base['features'](rows,rr,2026,ident);fb=base['features'](rows,rr,2026,ident,True)
  xs.append({'id':ident,'year':2026,'role':rr,'x':f,'bounded_x':fb,'history_override':rows});source.append(z)
 preds=predict(models[rr],xs,2026)
 for i,z in enumerate(source):
  p=base['old'].players[z['id']];ps,audit=base['m'].paths(p);states=base['v'].mlb_role_paths(p,rr)[1]['outcome_state_projections']
  variants={}
  for method in METHODS:
   factor=float(preds[method][i])/z['baseline']['IP'];candidate={k:v*factor for k,v in z['baseline'].items()}
   for k in ['SV','HLD']:candidate[k]=z['baseline'].get(k,0)*min(1,factor)
   new=[(pr,list(path)) for pr,path in ps]
   for j in range(3):
    stats={k:v*factor for k,v in states[j][0].items()}
    for k in ['SV','HLD']:stats[k]=states[j][0].get(k,0)*min(1,factor)
    new[j][1][0]=base['r'].utility(base['r'].surplus(stats,rr))
   fits={mode:base['m'].competitive(new,mode)['display'] for mode in base['r'].MODES}
   variants[method]={'stats':candidate,'neutral':fits['neutral'],'competitive_fit':fits}
  impact.append({'id':z['id'],'name':z['name'],'role':rr,'age':z['age'],'baseline':z['baseline'],'baseline_neutral':z['baseline_neutral'],'prior_quality_candidate':z['candidate'],'prior_quality_neutral':z['candidate_neutral'],'selected':chosen,'variants':variants})
 print('Current completed',rr,len(source),flush=True)
(OUT/'Conditional_SP_Current_Impact.json.gz').write_bytes(gzip.compress(json.dumps(impact).encode(),mtime=0))
print('Follow-up saved',len(impact),flush=True)

"""General role-opportunity experiment using verified MiLB appearance shares, not talent."""
import sys,json,gzip,copy,collections
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
OUT=Path(__file__).resolve().parent;main=OUT/'opportunity_models.py';source=main.read_text();env={'__file__':str(main),'__name__':'role_helpers'}
exec(compile(source.split('devscores={};test=[];selected={};training_manifest=[]')[0],str(main),'exec'),env)
records,index,first,lookup,settings=(env[k] for k in ['records','index','first','lookup','SETTINGS']);saved=json.loads(gzip.decompress((OUT/'Opportunity_Test_Cases.json.gz').read_bytes()));savedby={(z['mlbam_id'],z['anchor'],z['role']):z for z in saved if z['role']!='H'}
def minor_share(ident,year):
 parts=index.get((ident,year),[]);gp=sum(z.get('games') or 0 for z in parts);gs=sum(z.get('starts') or 0 for z in parts)
 return gs/gp if gp else 0
def xrow(z):
 rows=z.get('history_override',env['hist'].get((z['id'],'P'),[]))
 f=env['forecast'](rows,z['role'],z['year'],z['id'],strict=True);rates=f[0] if f else env['old'].prior[z['role']]
 return np.r_[z['bounded_x'],minor_share(z['id'],first.get(z['id'])),minor_share(z['id'],z['year']),*[rates.get(k,0) for k in ['K','ER','BB','H','QA3','SV','HLD']]]
def fit(train):
 X=np.stack([xrow(z) for z in train]);y=np.array([z['target'] for z in train]);labels=np.array([0 if z['target']==0 else 2 if lookup.get((z['id'],z['year']+1,'P'),{}).get('role')=='SP' else 1 for z in train]);classifier=HistGradientBoostingClassifier(**settings).fit(X,labels);regs={}
 for label in [1,2]:
  keep=labels==label
  if keep.any():regs[label]=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[keep],y[keep])
 return classifier,regs,dict(collections.Counter(map(int,labels)))
def predict(models,rows,cap):
 classifier,regs,counts=models;X=np.stack([xrow(z) for z in rows]);p=classifier.predict_proba(X);out=np.zeros(len(rows));parts={}
 for col,label in enumerate(classifier.classes_):
  parts[int(label)]=p[:,col]
  if label in regs:out+=p[:,col]*np.maximum(0,regs[label].predict(X))
 return np.minimum(cap,out),parts
cases=[];manifest=[]
for rr in ['SP','RP']:
 for year in env['ANCHORS']:
  train=env['training'](rr,year);xs=[z for z in records[rr] if z['year']==year and (z['id'],year,rr) in savedby]
  if not xs:continue
  models=fit(train);pred,prob=predict(models,xs,env['cap_at'](rr,year));manifest.append({'role':rr,'anchor':year,'training_classes':models[2],'latest_training_target':max(z['year']+1 for z in train)})
  for j,z in enumerate(xs):
   q=savedby[z['id'],year,rr];ratio=pred[j]/q['baseline']['IP'];stat={k:value*ratio for k,value in q['baseline'].items()}
   for k in ['SV','HLD']:stat[k]=q['baseline'].get(k,0)*min(1,ratio)
   targetrole=lookup.get((z['id'],year+1,'P'),{}).get('role','absent');cases.append(q|{'role_aware':stat,'future_role_observed_for_scoring_only':targetrole,'probability_next_SP':float(prob.get(2,np.zeros(len(xs)))[j]),'probability_next_RP':float(prob.get(1,np.zeros(len(xs)))[j])})
def scores(xs):
 result={}
 for group in sorted({g for z in xs for g in z['groups']}):
  rows=[z for z in xs if group in z['groups']];result[group]={'n':len(rows),'metrics':{}}
  for k in ['IP','K','ER','BB','H','QA3']:
   result[group]['metrics'][k]={method:{'MAE':float(np.mean([abs(z[method].get(k,0)-z['actual'].get(k,0)) for z in rows])),'bias':float(np.mean([z[method].get(k,0)-z['actual'].get(k,0) for z in rows]))} for method in ['baseline','selected','role_aware']}
 return result
for z in cases:
 z['groups']=z['groups']+['next_role_'+z['future_role_observed_for_scoring_only']]
(OUT/'Quality_Aware_Validation.json').write_text(json.dumps({'scores':scores(cases),'manifest':manifest,'features_added':['debut_MiLB_GS_GP','current_MiLB_GS_GP','MLB_only_K_ER_BB_H_QA3_SV_HLD_rates'],'talent':'All performance rates remain frozen MLB-only; additional inputs are appearance-role evidence only.'},indent=2));(OUT/'Quality_Aware_Cases.json.gz').write_bytes(gzip.compress(json.dumps(cases,separators=(',',':')).encode(),mtime=0))
prior=json.loads((OUT.parent/'Historical_Cases.json').read_text());by={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
for z in prior:
 q=copy.deepcopy(by[z['mlbam_id'],z['anchor']]);factor=q['role_aware']['IP']/z['baseline']['IP'];q['baseline']=z['baseline'];q['role_aware']={k:value*factor for k,value in z['baseline'].items()}
 selectedfactor=q['selected']['IP']/z['baseline']['IP'];q['selected']={k:value*selectedfactor for k,value in z['baseline'].items()}
 for k in ['SV','HLD']:
  q['role_aware'][k]=z['baseline'].get(k,0)*min(1,factor);q['selected'][k]=z['baseline'].get(k,0)*min(1,selectedfactor)
 frozen.append(q)
(OUT/'Quality_Aware_Frozen94.json').write_text(json.dumps(scores(frozen),indent=2))
# Current diagnostic comparisons for every modeled pitcher, values/competitive fit first year only.
models={rr:fit(env['training'](rr,2026)) for rr in ['SP','RP']};current=json.loads(gzip.decompress((OUT/'Opportunity_Current_Impact.json.gz').read_bytes()));impact=[]
for z in current:
 st=z['streams'][0];rr=st['role']
 if rr not in models:continue
 asset=next(a for a in env['catalog']['assets'] if a['id']==z['id']);p=env['old'].players[z['id']];ident=env['v'].cf.IDS.get(z['id'],p.get('mlbamId'));rows=env['v'].seasons(p,rr)
 f=env['features'](rows,rr,2026,ident);fb=env['features'](rows,rr,2026,ident,True);row={'id':ident,'year':2026,'role':rr,'x':f,'bounded_x':fb,'history_override':rows};prediction,prob=predict(models[rr],[row],env['cap_at'](rr,2026));factor=float(prediction[0])/st['baseline']['IP'];candidate={k:value*factor for k,value in st['baseline'].items()}
 for k in ['SV','HLD']:candidate[k]=st['baseline'].get(k,0)*min(1,factor)
 ps,audit=env['m'].paths(p);new=[(pr,list(path)) for pr,path in ps];states=env['v'].mlb_role_paths(p,rr)[1]['outcome_state_projections']
 for j in range(3):
  stats={k:value*factor for k,value in states[j][0].items()}
  for k in ['SV','HLD']:stats[k]=states[j][0].get(k,0)*min(1,factor)
  new[j][1][0]=env['r'].utility(env['r'].surplus(stats,rr))
 fitvalues={mode:env['m'].competitive(new,mode)['display'] for mode in env['r'].MODES};impact.append({'id':z['id'],'name':z['name'],'owner':z['owner'],'age':z['age'],'role':rr,'baseline':st['baseline'],'candidate':candidate,'probability_next_SP':float(prob.get(2,np.zeros(1))[0]),'probability_next_RP':float(prob.get(1,np.zeros(1))[0]),'baseline_neutral':z['baseline_neutral'],'candidate_neutral':fitvalues['neutral'],'baseline_competitive_fit':z['baseline_competitive_fit'],'candidate_competitive_fit':fitvalues})
(OUT/'Quality_Aware_Current_Impact.json.gz').write_bytes(gzip.compress(json.dumps(impact,indent=2).encode(),mtime=0));print('Quality-aware checks complete',len(cases),len(impact),flush=True)

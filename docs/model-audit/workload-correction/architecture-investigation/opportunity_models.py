"""Past-only expected MLB workload models; no player overrides or production writes."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,copy,csv,math,hashlib,gzip,collections,functools,ast
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from threadpoolctl import threadpool_limits
threadpool_limits(1)
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;PARENT=OUT.parent
sys.path.insert(0,str(PARENT))
# Reuse saved helpers only; do not execute completed collection or scoring loops.
helper=PARENT/'validate_debut.py';source=helper.read_text().split("methods=['baseline'")[0];env={'__file__':str(helper),'__name__':'debut_helpers'}
exec(compile(source,str(helper),'exec'),env)
m,v,r,old=(env[k] for k in ['m','v','r','old']);hist,lookup,first,index=(env[k] for k in ['hist','lookup','first','index']);forecast,project=env['forecast'],env['project'];catalog=env['catalog'];appear=env['appear']
minor={(ident,year):sum(z['outs'] for z in zs)/3 for (ident,year),zs in index.items()};complete=env['complete']
NAMES=['latest','lag1','lag2','lag3','calendar_mean','positive_mean','highest','lowest','stdev','positive_years','zero_years','durable_run','recent_change','age','years_since_debut','current_GP','current_GS','current_GS_fraction','previous_GS_fraction','debut_MLB_workload','debut_MiLB_workload','debut_professional_capacity','debut_MLB_share','capacity_missing','current_MiLB_workload','current_professional_capacity','role_changed','career_positive_seasons','age_x_latest']
METHODS=['ridge','direct_tree','hurdle','hurdle_no_capacity','hurdle_bounded2020']
CAPACITY_COLUMNS=[19,20,21,22,23,24,25]
SETTINGS={'max_iter':100,'max_leaf_nodes':15,'min_samples_leaf':30,'learning_rate':.07,'l2_regularization':10,'random_state':2309}
def age(ident,year):
 a=r.age_at(ident,year)
 return float(a) if a is not None and math.isfinite(a) else None
def features(rows,rr,year,ident,bounded=False):
 stream='H' if rr=='H' else 'P';past=[z for z in rows if z['year']<=year and r.exposure(z['stat'],rr)>0]
 if not past:return None
 by={z['year']:z for z in past};debut=min(z['year'] for z in past);a=age(ident,year)
 if a is None:return None
 def exposure(y):
  z=by.get(y);e=r.exposure(z['stat'],rr) if z else 0
  if bounded and y==2020:
   prior=[r.exposure(t['stat'],rr) for t in past if t['year']<2020]
   if prior:e=min(e*162/60,max(prior))
  return e
 work=[exposure(y) for y in range(year,year-4,-1)];pos=[x for x in work if x>0];run=0;threshold=600 if rr=='H' else 150 if rr=='SP' else 50
 for y in range(year,year-6,-1):
  z=by.get(y);e=r.exposure(z['stat'],rr) if z else 0
  # Schedule-aware durability classification, not synthesized talent or target counts.
  if e>=(threshold*60/162 if y==2020 else threshold):run+=1
  else:break
 current=by.get(year);previous=by.get(year-1);curinfo=appear.get((ident,year),{}) if rr!='H' else {};previnfo=appear.get((ident,year-1),{}) if rr!='H' else {}
 if current and year==2026 and rr!='H':curinfo=current.get('stat',{})
 gp=curinfo.get('GP',curinfo.get('gamesPlayed',0));gs=curinfo.get('GS',curinfo.get('gamesStarted',0));pg=previnfo.get('GP',0);ps=previnfo.get('GS',0)
 actualdebut=first.get(ident) if rr!='H' else debut;drow=by.get(actualdebut);di=r.exposure(drow['stat'],rr) if drow else 0
 verified=bool(rr!='H' and actualdebut and actualdebut<=year and complete.get(actualdebut,set())==set(range(11,17)))
 mi=minor.get((ident,actualdebut),0) if verified else 0;pro=di+mi;currentmi=minor.get((ident,year),0) if rr!='H' and complete.get(year,set())==set(range(11,17)) else 0
 x=[*work,float(np.mean(work)),float(np.mean(pos)) if pos else 0,max(pos) if pos else 0,min(pos) if pos else 0,float(np.std(work)),len(pos),sum(y>=debut and exposure(y)==0 for y in range(year-3,year+1)),run,work[0]-work[1],a,min(30,year-debut),gp,gs,gs/gp if gp else 0,ps/pg if pg else 0,di,mi,pro,di/pro if pro else 0,0 if verified or rr=='H' else 1,currentmi,work[0]+currentmi,int(bool(current and previous and current['role']!=previous['role'])),len(past),a*work[0]/100]
 assert len(x)==len(NAMES)
 return np.asarray(x,dtype=float)
def groups_for(rows,rr,year,ident):
 f=features(rows,rr,year,ident);a=f[13];g=['all',rr,'young' if a<=26 else 'established',f'anchor_{year}']
 if rr=='H':
  if f[11]>=4:g.append('durable_four_years')
  elif f[0]>=400:g.append('ordinary_regular')
  else:g.append('part_time_or_returning')
  if a>=33:g.append('aging_33plus')
  short=0
  for z in rows:
   if year-3<=z['year']<=year:
    threshold=400*60/162 if z['year']==2020 else 400
    short+=z['stat'].get('PA',0)<threshold
  if short>=2:g.append('repeated_shortfall_proxy_not_diagnosed_injury')
 else:
  debut=first.get(ident)
  if debut==year:g.append('first_MLB_season')
  if debut==year-1:g.append('second_MLB_season')
  if f[17]>0 and f[17]<1:g.append('swingmen')
  if f[20]>0 and debut and debut>=year-3:g.append('recent_debut_with_MiLB')
 return g
records={rr:[] for rr in ['H','SP','RP']}
for (ident,stream),rows in hist.items():
 earliest=min(z['year'] for z in rows)
 for year in range(max(2013,earliest),2025):
  recent=[z for z in rows if z['year']<=year and z['year']>=year-2 and r.exposure(z['stat'],'H' if stream=='H' else 'SP')>0]
  if not recent:continue
  latest=max(recent,key=lambda z:z['year']);rr=latest['role'];current=lookup.get((ident,year,stream))
  if stream=='H' and max(z['stat'].get('PA',0) for z in recent)<100:continue
  a=age(ident,year)
  if a is None:continue
  f=features(rows,rr,year,ident);fb=features(rows,rr,year,ident,True)
  target=lookup.get((ident,year+1,stream));actual=target['stat'] if target else {};y=r.exposure(actual,rr)
  records[rr].append({'id':ident,'year':year,'name':latest['name'],'role':rr,'x':f,'bounded_x':fb,'target':y,'actual':actual,'groups':groups_for(rows,rr,year,ident),'positive_anchor':bool(current and r.exposure(current['stat'],rr)>0)})
print('Records',{rr:len(xs) for rr,xs in records.items()},flush=True)
def fit(rows,method):
 X=np.stack([z['bounded_x'] if method=='hurdle_bounded2020' else z['x'] for z in rows]);y=np.asarray([z['target'] for z in rows])
 if method=='hurdle_no_capacity':X[:,CAPACITY_COLUMNS]=0
 if method=='ridge':model=make_pipeline(StandardScaler(),Ridge(alpha=100));model.fit(X,y);return model,None
 if method=='direct_tree':model=HistGradientBoostingRegressor(loss='squared_error',**SETTINGS);model.fit(X,y);return model,None
 active=y>0;participation=HistGradientBoostingClassifier(**SETTINGS);participation.fit(X,active)
 model=HistGradientBoostingRegressor(loss='squared_error',**SETTINGS);model.fit(X[active],y[active]);return model,participation
def predict(models,rows,method,cap):
 X=np.stack([z['bounded_x'] if method=='hurdle_bounded2020' else z['x'] for z in rows])
 if method=='hurdle_no_capacity':X[:,CAPACITY_COLUMNS]=0
 model,part=models;conditional=np.maximum(0,model.predict(X));prob=part.predict_proba(X)[:,1] if part is not None else np.ones(len(rows));means=np.minimum(cap,conditional*prob)
 return means,prob,conditional
def training(rr,anchor,development=False,raw_covid=False):
 return [z for z in records[rr] if z['year']+1<=anchor and z['id']%5 not in ([0,4] if development else [0]) and (raw_covid or z['year'] not in [2019,2020])]
@functools.lru_cache(None)
def cap_at(rr,anchor):
 vals=[r.exposure(z['stat'],rr) for z in old.AN if z['role']==rr and z['year']<=anchor and z['year']!=2020 and r.exposure(z['stat'],rr)>0]
 return float(np.quantile(vals,.995))
ANCHORS=[2016,2017,2018,2021,2022,2023,2024]
saved_pitch=json.loads((PARENT/'Debut_Chronological_Cases.json').read_text());preserved={(z['mlbam_id'],z['anchor']):z for z in saved_pitch}
devscores={};test=[];selected={};training_manifest=[]
for rr in ['H','SP','RP']:
 development={method:[] for method in METHODS}
 for year in [2016,2017,2018,2021,2022]:
  train=training(rr,year,True);dev=[z for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  if not dev:continue
  for method in METHODS:
   model=fit(train,method);pred,prob,cond=predict(model,dev,method,cap_at(rr,year));development[method].extend([(float(a),z['target']) for a,z in zip(pred,dev)])
 devscores[rr]={method:{'n':len(xs),'MAE':float(np.mean([abs(a-b) for a,b in xs])),'bias':float(np.mean([a-b for a,b in xs]))} for method,xs in development.items()}
 # Fixed selection objective chosen before scoring: MAE plus one-quarter absolute signed bias.
 selected[rr]=min(METHODS,key=lambda method:devscores[rr][method]['MAE']+.25*abs(devscores[rr][method]['bias']))
 print('Selected from development',rr,selected[rr],devscores[rr],flush=True)
 for year in ANCHORS:
  train=training(rr,year);xs=[z for z in records[rr] if z['year']==year and z['id']%5==0 and z['positive_anchor'] and (rr=='H' or (z['id'],year) in preserved)]
  if not xs:continue
  predictions={};modelmeta={}
  for method in METHODS:
   model=fit(train,method);pred,prob,cond=predict(model,xs,method,cap_at(rr,year));predictions[method]=pred;modelmeta[method]=(prob,cond)
  training_manifest.append({'role':rr,'forecast_anchor':year,'train_rows':len(train),'train_id_mods':sorted({z['id']%5 for z in train}),'latest_training_target':max(z['year']+1 for z in train),'test_n':len(xs),'cap':cap_at(rr,year)})
  for j,z in enumerate(xs):
   rows=hist[z['id'],'H' if rr=='H' else 'P'];base=forecast(rows,rr,year,z['id'],strict=True)
   if not base:continue
   baseline=preserved[z['id'],year]['baseline'] if rr!='H' else project(base,rr,z['x'][13],year,True)
   exposure=baseline.get('PA' if rr=='H' else 'IP',0);result={'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':rr,'groups':z['groups'],'actual':z['actual'],'baseline':baseline,'chosen_method':selected[rr]}
   for method in METHODS:
    expected=float(predictions[method][j]);ratio=expected/exposure if exposure else 0;stat={k:value*ratio for k,value in baseline.items()}
    if rr!='H':
     for k in ['SV','HLD']:stat[k]=baseline.get(k,0)*min(1,ratio) # separate opportunity forecast, no workload-created leverage
     stat['QA3']=min(stat.get('QA3',0),stat['IP']/5)
    else:stat=v.reconcile(stat)
    result[method]=stat
   result['selected']=result[selected[rr]];test.append(result)
 print('Completed test role',rr,flush=True)
def scores(cases):
 out={}
 for group in sorted({g for z in cases for g in z['groups']}):
  xs=[z for z in cases if group in z['groups']];metrics={}
  for k in ['PA','IP','K','ER','BB','H','QA3','HR','R','RBI','SB','SV','HLD']:
   valid=[z for z in xs if k in z['baseline'] and (k in z['actual'] or not z['actual'])]
   if not valid:continue
   metrics[k]={}
   for method in ['baseline',*METHODS,'selected']:
    errors=np.asarray([z[method].get(k,0)-z['actual'].get(k,0) for z in valid]);metrics[k][method]={'n':len(valid),'MAE':float(np.mean(np.abs(errors))),'bias':float(np.mean(errors)),'RMSE':float(np.sqrt(np.mean(errors**2)))}
  out[group]={'n':len(xs),'metrics':metrics}
 return out
result={'methods':METHODS,'selected_by_development':selected,'development_scores':devscores,'test_scores':scores(test),'pitcher_test_case_count':sum(z['role']!='H' for z in test),'hitter_test_case_count':sum(z['role']=='H' for z in test),'training_manifest':training_manifest,'features':NAMES,'settings':SETTINGS,'selection_rule':'Development MAE +.25absolute bias; no test-label selection','covid_training_policy':'Exclude2019 anchors(target2020) and2020 anchors; bounded variant changes2020 workload features only','saved_baseline_reused':True}
assert result['pitcher_test_case_count']==1084
(OUT/'Opportunity_Validation.json').write_text(json.dumps(result,indent=2));(OUT/'Opportunity_Test_Cases.json.gz').write_bytes(gzip.compress(json.dumps(test,separators=(',',':')).encode(),mtime=0))
print('Historical testing saved',flush=True)
# Exact original94 benchmark subset, reuse baseline as originally frozen; scale category rates from saved baseline.
frozen94=json.loads((PARENT/'Historical_Cases.json').read_text());testby={(z['mlbam_id'],z['anchor']):z for z in test if z['role']!='H'};frozen=[]
for z in frozen94:
 t=testby[z['mlbam_id'],z['anchor']];o=t|{'baseline':z['baseline'],'groups':z['subgroups']}
 for method in [*METHODS,'selected']:
  expected=t[method]['IP'];ratio=expected/z['baseline']['IP'];o[method]={k:value*ratio for k,value in z['baseline'].items()}
  for k in ['SV','HLD']:o[method][k]=z['baseline'].get(k,0)*min(1,ratio)
 frozen.append(o)
(OUT/'Opportunity_Frozen94.json').write_text(json.dumps(scores(frozen),indent=2))
# Current impact, first-year only; prospects, picks, uncertain identities keep original paths.
currentalternatives={rr:{method:fit(training(rr,2026),method) for method in METHODS} for rr in ['H','SP','RP']}
currentmodels={rr:currentalternatives[rr][selected[rr]] for rr in ['H','SP','RP']};current=[];unchanged=[];maxbaseline=0
def component(audit,rr):
 audit=audit.get('MLB',audit);z=audit.get('two_way_components',{}).get(rr,audit);return z.get('audit',z)
for asset in catalog['assets']:
 p=old.players.get(asset['id']);ident=v.cf.IDS.get(asset['id'],p.get('mlbamId') if p else None)
 if not p or not ident or not asset.get('audit',{}).get('MLB',asset.get('audit',{})).get('projection'):
  unchanged.append({'id':asset['id'],'reason':'Pick/prospect/unresolved or no modeled MLB projection'});continue
 roles=['H',v.role(p)] if asset['audit'].get('role')=='H+SP' else [v.role(p)];changedstreams=[];originalpaths,audit=m.paths(p);newpaths=[(prob,list(path)) for prob,path in originalpaths]
 for rr in roles:
  if rr not in currentmodels:continue
  rows=v.seasons(p,rr);f=v.recent_forecast(p,rr)
  if not f:continue
  x=features(rows,rr,2026,ident);xb=features(rows,rr,2026,ident,True)
  if x is None:continue
  d={'x':x,'bounded_x':xb};method=selected[rr];pred,prob,cond=predict(currentmodels[rr],[d],method,cap_at(rr,2026));baseau=component(asset['audit'],rr);baseprojection=baseau['projection'];exposure=baseprojection.get('PA' if rr=='H' else 'IP',0);expected=float(pred[0]);factor=expected/exposure if exposure else 0
  baseline_states=v.mlb_role_paths(p,rr)[1]['outcome_state_projections'];newstates=[]
  for states in baseline_states:
   st={k:value*factor for k,value in states[0].items()}
   if rr!='H':
    for k in ['SV','HLD']:st[k]=states[0].get(k,0)*min(1,factor)
    st['QA3']=min(st['QA3'],st['IP']/5)
   else:st=v.reconcile(st)
   newstates.append(st)
  utilities=[r.utility(r.surplus(st,rr)) for st in newstates]
  if len(roles)==1:
   # MLB atoms precede retained prospect atoms in the preserved mixture.
   # Change only the three MLB states; keep prospect paths and mixture weights intact.
   assert len(newpaths)>=3
   for j in range(3):newpaths[j][1][0]=utilities[j]
  candidate={k:value*factor for k,value in baseprojection.items()}
  if rr!='H':
   for k in ['SV','HLD']:candidate[k]=baseprojection.get(k,0)*min(1,factor)
   candidate['QA3']=min(candidate['QA3'],candidate['IP']/5)
  else:candidate=v.reconcile(candidate)
  changedstreams.append({'role':rr,'method':method,'baseline':baseprojection,'candidate':candidate,'expected_MLB_workload':expected,'participation_probability':float(prob[0]),'conditional_workload':float(cond[0]),'features':dict(zip(NAMES,map(float,x))),'MLB_talent_rates_unchanged':True,'rate_aging_unchanged':True,'later_years_unchanged':True})
 if len(roles)>1:
  unchanged.append({'id':asset['id'],'reason':'Two-way streams audited; combined valuation kept frozen pending overlap/distribution validation','experimental_streams':changedstreams});continue
 if not changedstreams:
  unchanged.append({'id':asset['id'],'reason':'No supported MLB workload features'});continue
 for (oldprob,oldpath),(newprob,newpath) in zip(originalpaths,newpaths):
  assert oldprob==newprob and oldpath[1:]==newpath[1:]
 assert originalpaths[3:]==newpaths[3:]
 baselinefit={mode:m.competitive(originalpaths,mode) for mode in r.MODES};candidatefit={mode:m.competitive(newpaths,mode) for mode in r.MODES};maxbaseline=max(maxbaseline,abs(baselinefit['neutral']['display']-asset['values']['neutral']['display']))
 alternatives={}
 for variant in METHODS:
  vp,vprob,vcond=predict(currentalternatives[rr][variant],[d],variant,cap_at(rr,2026));vratio=float(vp[0])/exposure;vstates=[]
  for states in baseline_states:
   st={k:value*vratio for k,value in states[0].items()}
   if rr!='H':
    for k in ['SV','HLD']:st[k]=states[0].get(k,0)*min(1,vratio)
   else:st=v.reconcile(st)
   vstates.append(st)
  vpaths=[(pr,list(path)) for pr,path in originalpaths]
  for j in range(3):vpaths[j][1][0]=r.utility(r.surplus(vstates[j],rr))
  vs={k:value*vratio for k,value in baseprojection.items()}
  if rr!='H':
   for k in ['SV','HLD']:vs[k]=baseprojection.get(k,0)*min(1,vratio)
  else:vs=v.reconcile(vs)
  alternatives[variant]={'projection':vs,'neutral':m.competitive(vpaths,'neutral')['display'],'competitive_fit':{mode:m.competitive(vpaths,mode)['display'] for mode in r.MODES},'participation_probability':float(vprob[0]),'conditional_workload':float(vcond[0])}
 assert abs(alternatives[selected[rr]]['neutral']-candidatefit['neutral']['display'])<1e-8
 current.append({'id':asset['id'],'name':asset['name'],'owner':asset['owner'],'age':p.get('age'),'streams':changedstreams,'baseline_neutral':asset['values']['neutral']['display'],'candidate_neutral':candidatefit['neutral']['display'],'baseline_competitive_fit':{k:z['display'] for k,z in baselinefit.items()},'candidate_competitive_fit':{k:z['display'] for k,z in candidatefit.items()},'value_delta':candidatefit['neutral']['display']-asset['values']['neutral']['display'],'alternatives':alternatives})
 print('',end='',flush=True)
(OUT/'Opportunity_Current_Impact.json.gz').write_bytes(gzip.compress(json.dumps(current,indent=2).encode(),mtime=0));(OUT/'Unaffected_Assets.json.gz').write_bytes(gzip.compress(json.dumps(unchanged,indent=2).encode(),mtime=0))
csvrows=[]
for z in current:
 st=z['streams'][0];key='PA' if st['role']=='H' else 'IP';delta=st['candidate'][key]-st['baseline'][key]
 if abs(delta)<(10 if key=='PA' else 1) and abs(z['value_delta'])<1:continue
 row={'id':z['id'],'player':z['name'],'fantasy_organization':'Island' if z['owner'].casefold()=='epskenes island' else z['owner'],'age':z['age'],'role':st['role'],'method':st['method'],'participation_probability':st['participation_probability'],'conditional_workload':st['conditional_workload'],'baseline_neutral':z['baseline_neutral'],'candidate_neutral':z['candidate_neutral'],'value_delta':z['value_delta']}
 for k in ['PA','IP','K','ER','BB','H','QA3','HR','R','RBI','SB','SV','HLD']:row['baseline_'+k]=st['baseline'].get(k);row['candidate_'+k]=st['candidate'].get(k)
 for mode in r.MODES:row['baseline_fit_'+mode]=z['baseline_competitive_fit'][mode];row['candidate_fit_'+mode]=z['candidate_competitive_fit'][mode]
 csvrows.append(row)
with (OUT/'Opportunity_Material_Impact.csv').open('w') as file:
 w=csv.DictWriter(file,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
reg={'asset_count':len(catalog['assets']),'current_modeled_changed':len(current),'untouched':len(unchanged),'original_catalog_sha256':hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),'max_baseline_value_reproduction_error':maxbaseline,'production_changes':False,'all_IDs_owners_picks_unchanged':True,'experimental_first_year_only':True,'MLB_talent_and_rate_aging_unchanged':True,'save_hold_totals_never_increased':True,'two_way_valuation_held_frozen':True,'later_years_and_prospect_paths_unchanged':True,'uncertainty_distribution':'Frozen mean-one states rescaled; not recalibrated, no probabilistic superiority claim'}
assert len(current)+len(unchanged)==2546;assert maxbaseline<1e-7
(OUT/'Opportunity_Regression.json').write_text(json.dumps(reg,indent=2));print('DONE',reg,flush=True)

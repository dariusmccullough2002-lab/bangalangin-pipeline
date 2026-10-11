"""One frozen state-severity calibration; never modifies immutable parent models."""
import sys,os,importlib.util,json,gzip,csv,hashlib,copy
from pathlib import Path
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,joblib
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('preserved_calibration',D.parent/'calibration-starter/run.py');parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
r=parent.r;e=parent.e;s=parent.s;STATES=r.STATES
protocol=json.loads((D/'Protocol_Freeze.json').read_text());assert protocol['candidate'].startswith('Only demonstrated starter retained_reduced')
BASE=parent.BASE;ART={};EXCLUDED=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids'])
def put(name,v):
 b=json.dumps(v,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x).encode();(D/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
def artifact(asof):
 if asof in ART:return ART[asof]
 path=D/f'severity-P-{asof}.joblib'
 if path.exists():ART[asof]=joblib.load(path);return ART[asof]
 model=parent.base_model(asof,'P');rows=[a for a in e.training(asof,calendar=False,family='P') if a['year']!=2020 and a['z']['id']%5==4 and a['z']['id'] not in EXCLUDED and s.forecast_role(a['z'])[0]=='starter' and s.target_label(a['z'])['state']==2]
 residuals=[];weights=[];log=[]
 for a in rows:
  z=a['z'];assert z['id']%5==4 and a['year']<=min(asof,2025)
  with r.prediction_only(z):c=r.predict(model,z)
  mean=c['fitted']['full_role_workload']*c['fitted']['ratios']['retained_reduced'];res=a['raw_value']-mean;residuals.append(res);weights.append(a['weight']);log.append({'id':z['id'],'anchor':z['year'],'target':a['year'],'actual_IP':a['raw_value'],'parent_reduced_IP':mean,'residual':res,'weight':a['weight']})
 eligible=len(rows)>=60;offset=float(np.average(residuals,weights=weights)) if eligible else 0.
 v={'asof':asof,'n':len(rows),'offset_IP':offset,'applied':eligible,'fallback':None if eligible else 'fewer than60 starter retained-reduced calibration rows','latest_target':max((a['year'] for a in rows),default=None),'IDmods':[4] if rows else [],'parent_sha256':hashlib.sha256((parent.C/f'model-P-{asof}.joblib').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((D/'Protocol_Freeze.json').read_bytes()).hexdigest(),'calibration_rows':log};joblib.dump(v,path,compress=3);ART[asof]=v;print('FIT_SEVERITY',asof,len(rows),offset,flush=True);return v

def apply(prob,means,role,asof):
 new=dict(means);v=artifact(asof) if role=='starter' else None
 if v is not None:new['retained_reduced']=float(np.clip(means['retained_reduced']+v['offset_IP'],0,251))
 expected=sum(prob[k]*new[k] for k in STATES);delta=sum(prob[k]*(new[k]-means[k]) for k in STATES)
 return expected,new,delta,v

def metrics(xs):
 out=[];years=[];cal=[];within=[];decomp=[]
 for fam in ['H','P']:
  fs=[a for a in xs if (a['role']=='H')==(fam=='H')];groups={g for a in fs for g in a['groups']}|({'demonstrated_starter','demonstrated_reliever','demonstrated_swingman'} if fam=='P' else set())
  for group in sorted(groups):
   ys=[a for a in fs if a['repaired_forecast_role']==group.replace('demonstrated_','')] if group.startswith('demonstrated_') else [a for a in fs if group in a['groups']]
   if not ys:continue
   for method in ['frozen_hybrid','five_retrained','direct_retrained','severity_candidate']:out.append({'family':fam,'cohort':group,'model':method,**e.metric([(a[method],a['actual']) for a in ys])})
   cal.append({'family':fam,'cohort':group,'n':len(ys),'joint_Brier_parent_and_candidate':float(np.mean([sum((a['retrained_probabilities'][st]-int(a['repaired_actual_state']==st))**2 for st in STATES) for a in ys])),'participation_Brier_parent_and_candidate':float(np.mean([((1-a['retrained_probabilities']['absent'])-int(a['actual']>0))**2 for a in ys]))})
   for st in STATES:
    obs=[a for a in ys if a['repaired_actual_state']==st];within.append({'family':fam,'cohort':group,'state':st,'n':len(ys),'state_n':len(obs),'predicted_frequency':float(np.mean([a['retrained_probabilities'][st] for a in ys])),'observed_frequency':len(obs)/len(ys),'parent_within_state_bias':float(np.mean([a['retrained_state_means'][st]-a['actual'] for a in obs])) if obs else None,'candidate_within_state_bias':float(np.mean([a['candidate_state_means'][st]-a['actual'] for a in obs])) if obs else None})
   for method in ['parent','candidate']:
    decomp.append({'family':fam,'cohort':group,'model':method,'n':len(ys),**{f'{k}_{metric}':float(np.mean([abs(a[f'{method}_{k}']) if metric=='MAE' else a[f'{method}_{k}'] for a in ys])) for k in ['frequency_error','severity_error'] for metric in ['MAE','bias']}})
  for year in sorted({a['anchor'] for a in fs}):
   for group in ['all','starter'] if fam=='P' else ['all']:
    ys=[a for a in fs if a['anchor']==year and (group=='all' or a['repaired_forecast_role']=='starter')]
    if ys:
     for method in ['frozen_hybrid','five_retrained','severity_candidate']:years.append({'family':fam,'anchor':year,'cohort':group,'model':method,**e.metric([(a[method],a['actual']) for a in ys])})
 write('Validation.csv',out);write('Year_Validation.csv',years);write('Calibration.csv',cal);write('State_Frequencies_Severity.csv',within);write('Error_Attribution.csv',decomp)
 oldD=r.p.D;r.p.D=D;r.p.gates([a|{'direct_mean':a['severity_candidate']} for a in xs]);r.p.D=oldD

def evaluate():
 out=[];flat=[]
 for a in BASE:
  role=a['repaired_forecast_role'];expected,new,delta,v=apply(a['retrained_probabilities'],a['retrained_state_means'],role,a['anchor']) if a['role']!='H' else (a['five_retrained'],dict(a['retrained_state_means']),0,None)
  assert abs(expected-(a['five_retrained']+delta))<1e-8
  state=a['repaired_actual_state'];parent_sev=a['retrained_state_means'][state]-a['actual'];new_sev=new[state]-a['actual'];parent_freq=a['five_retrained']-a['actual']-parent_sev;new_freq=expected-a['actual']-new_sev
  row=a|{'severity_candidate':expected,'candidate_state_means':new,'state_mean_only_delta':delta,'parent_frequency_error':parent_freq,'parent_severity_error':parent_sev,'candidate_frequency_error':new_freq,'candidate_severity_error':new_sev,'evaluation_status':'exposed exploratory'};out.append(row)
  flat.append({k:a[k] for k in ['mlbam_id','name','anchor','target_season','role','actual','frozen_hybrid','five_retrained','direct_retrained','repaired_forecast_role','repaired_actual_state']}|{'severity_candidate':expected,'parent_reduced_IP':a['retrained_state_means']['retained_reduced'],'candidate_reduced_IP':new['retained_reduced'],'offset_IP':v['offset_IP'] if v else 0,'p_reduced':a['retrained_probabilities']['retained_reduced'],'delta':delta,'groups':'|'.join(a['groups']),**{k:row[k] for k in ['parent_frequency_error','parent_severity_error','candidate_frequency_error','candidate_severity_error']}})
 put('Cases.json.gz',out);write('Chronological_Player_Comparisons.csv',flat);metrics(out);return out

def current():
 before=list(csv.DictReader((parent.C/'League_1900_Comparison.csv').open()));assets={a['id']:a for a in e.read(D.parent/'targeted-repair/Repair_League.json.gz')};diag=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);out=[];components=[]
 for a in before:
  z=e.current_z(assets[a['id']]) if hasattr(e,'current_z') else None
  if z is None:
   hs=e.v.seasons(e.old.players[a['id']],a['role']);z={'id':int(a['mlbam_id']),'year':2026,'role':a['role'],'history_override':hs,'x':e.base['features'](hs,a['role'],2026,int(a['mlbam_id'])),'bounded_x':e.base['features'](hs,a['role'],2026,int(a['mlbam_id']),True)}
  model=parent.base_model(2026,'H' if a['role']=='H' else 'P')
  with r.prediction_only(z):c=r.predict(model,z)
  means={'absent':0}|{k:c['fitted']['full_role_workload']*v for k,v in c['fitted']['ratios'].items()};p=c['probabilities'];role=c['role']
  new,nm,delta,v=apply(p,means,role,2026) if a['role']!='H' else (c['fitted']['expected'],means,0,None)
  assert abs(c['fitted']['expected']-float(a['five_retrained']))<1e-7
  q=1-p['absent'];row=a|{'forecast_role':role,'severity_candidate':new,'parent_unconditional':c['fitted']['expected'],'parent_given_active':c['fitted']['conditional_active'],'candidate_given_active':new/q if q else 0,'participation':q,'role_retention_given_active':c['role_retention_given_active'],'full_role_GS':c['fitted']['slots'].get('GS'),'full_role_RA':c['fitted']['slots'].get('RA'),'full_role_IP_PA':c['fitted']['full_role_workload'],'starter_IP_per_start':s.depths(z)[0] if a['role']!='H' else None,'severity_offset_IP':v['offset_IP'] if v else 0,'delta':delta,'allocator_adjustment':0,'medical_adjustment':0,'full_role_not_valuation_input':True,'fallback':v['fallback'] if v else 'unchanged nonstarter or hitter'}
  for st in STATES:row['p_'+st]=p[st];row['parent_mean_'+st]=means[st];row['candidate_mean_'+st]=nm[st]
  out.append(row);components.append({'id':a['id'],'parent':c,'candidate_state_means':nm,'candidate_unconditional':new})
 assert len(out)==1900;write('League_1900_Comparison.csv',out);write('Diagnostic_12_Comparisons.csv',[a for a in out if int(a['mlbam_id']) in diag]);put('League_Components.json.gz',components)
 return out
if __name__=='__main__':
 xs=evaluate();current();put('Fit_Manifests.json',[{k:v for k,v in a.items() if k!='calibration_rows'} for a in ART.values()]);print('COMPLETE ONE FROZEN SEVERITY TEST',flush=True)

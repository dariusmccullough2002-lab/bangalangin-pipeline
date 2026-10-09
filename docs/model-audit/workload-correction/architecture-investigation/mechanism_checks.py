"""Reuse completed benchmarks; clean MiLB ablation, pandemic training and exact workload trace."""
import sys,json,gzip,copy,math,functools,csv,hashlib
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;main=OUT/'opportunity_models.py';source=main.read_text();env={'__file__':str(main),'__name__':'opportunity_helpers'}
exec(compile(source.split('devscores={};test=[];selected={};training_manifest=[]')[0],str(main),'exec'),env)
m,v,r,old,hist,lookup,records,fit,predict,cap_at=(env[k] for k in ['m','v','r','old','hist','lookup','records','fit','predict','cap_at'])
test=json.loads(gzip.decompress((OUT/'Opportunity_Test_Cases.json.gz').read_bytes()));testby={(z['mlbam_id'],z['anchor'],z['role']):z for z in test};variants=['no_MiLB_only','raw_pandemic_training','normalized_pandemic_training'];comparisons=[]
def transform(z,variant,rr,year):
 z=z.copy();x=z['x'].copy()
 if variant=='no_MiLB_only':
  x[20]=0;x[21]=x[19];x[22]=1 if x[19]>0 else 0;x[24]=0;x[25]=x[0]
 elif variant=='normalized_pandemic_training':
  x=z['bounded_x'].copy()
  if z['year']==2019:z['target']=min(cap_at(rr,year),z['target']*162/60)
 z['x']=x;return z
for rr in ['H','SP','RP']:
 for year in env['ANCHORS']:
  xs=[z for z in records[rr] if (z['id'],year,rr) in testby and z['year']==year]
  if not xs:continue
  pred={}
  for variant in variants:
   train=[transform(z,variant,rr,year) for z in records[rr] if z['year']+1<=year and z['id']%5!=0 and (variant!='no_MiLB_only' or z['year'] not in [2019,2020])]
   transformed=[transform(z,variant,rr,year) for z in xs];model=fit(train,'hurdle');pred[variant]=predict(model,transformed,'hurdle',cap_at(rr,year))[0]
  for j,z in enumerate(xs):
   q=testby[z['id'],year,rr];key='PA' if rr=='H' else 'IP';comparisons.append({'mlbam_id':z['id'],'anchor':year,'role':rr,'groups':q['groups'],'actual':q['actual'].get(key,0),'baseline':q['baseline'][key],'hurdle':q['hurdle'][key],'hurdle_bounded2020':q['hurdle_bounded2020'][key],**{variant:float(pred[variant][j]) for variant in variants}})
def scores(rows):
 out={}
 for group in sorted({g for z in rows for g in z['groups']}):
  out[group]={}
  for rr in ['H','SP','RP']:
   xs=[z for z in rows if z['role']==rr and group in z['groups']]
   if not xs:continue
   out[group][rr]={'n':len(xs),'metrics':{method:{'MAE':float(np.mean([abs(z[method]-z['actual']) for z in xs])),'bias':float(np.mean([z[method]-z['actual'] for z in xs]))} for method in ['baseline','hurdle','hurdle_bounded2020',*variants]}}
 return out
(OUT/'Mechanism_Validation.json').write_text(json.dumps({'scores':scores(comparisons),'no_MiLB_ablation':'Remove only MiLB totals; retain MLB debut opportunity evidence. Earlier no_capacity ablation also removed debut MLB evidence, so it is not a clean MiLB causal comparison.','pandemic_training':'Raw includes actual2020 target/anchor; normalized changes known historical2020 target workload and bounded features. No future pandemic schedule is predicted at2019.'},indent=2));(OUT/'Mechanism_Cases.json.gz').write_bytes(gzip.compress(json.dumps(comparisons).encode(),mtime=0))
# Trace current default: exact prior and survival path; no 2020 season in first-year training horizons.
traces=[]
for name in ['Matt Olson','Jacob Misiorowski','Nolan McLean','Cade Smith']:
 a=next(z for z in env['catalog']['assets'] if z['name']==name);p=old.players[a['id']];rr=v.role(p);f=v.recent_forecast(p,rr);rates,work,audit=f;age=int(round(p['age']));q=int(np.searchsorted(v.base.CUTS[rr],r.surplus({k:x*work for k,x in rates.items()},rr)/work*r.REFERENCE[rr]));curve=v.curve(rr,age,q);band=curve['age_band'];sample=[z for z in v.base.cohorts[rr] if (band is None or abs(z['age']-age)<=band) and (band is None or z['quality_bin']==q)]
 before=sum(r.exposure(z['anchor'],rr) for z in sample);after=sum(r.exposure(v.base.annual((v.HISTORY_H if rr=='H' else v.HISTORY_P).get((z['id'],z['year']+1))),rr) for z in sample)
 zeros=sum(not (v.HISTORY_H if rr=='H' else v.HISTORY_P).get((z['id'],z['year']+1)) for z in sample);blend=.7*audit['recent_workload']+.3*audit['healthy_observed_workload'];priorpull=(1-audit['prior_weight'])*blend+audit['prior_weight']*audit['role_workload_prior']
 traces.append({'name':name,'role':rr,'snapshot_age':p['age'],'recent_workload':audit['recent_workload'],'healthy_workload':audit['healthy_observed_workload'],'blend_before_prior':blend,'role_prior':audit['role_workload_prior'],'prior_weight':audit['prior_weight'],'prior_pull_loss':blend-priorpull,'role_cap':v.cf.cap(rr),'cap_loss':priorpull-work,'starting_workload':work,'first_year_attrition_factor':curve['path'][0]['workload'],'first_year_loss':work*(1-curve['path'][0]['workload']),'final_workload':work*curve['path'][0]['workload'],'curve_anchor_n':len(sample),'curve_unique_players':len({z['id'] for z in sample}),'curve_anchor_workload_sum':before,'next_year_workload_sum':after,'zero_next_year_anchors':zeros,'first_year_target_seasons':sorted({z['year']+1 for z in sample}),'COVID_in_first_year_curve':any(z['year']+1==2020 for z in sample),'first_year_factor_is_horizon':1,'extra_medical_penalty':False})
(OUT/'Exact_Workload_Traces.json').write_text(json.dumps(traces,indent=2))
print('Mechanism checks complete',flush=True)

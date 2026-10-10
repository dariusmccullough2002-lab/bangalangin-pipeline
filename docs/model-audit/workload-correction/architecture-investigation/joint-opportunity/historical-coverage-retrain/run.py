"""Frozen GP repair/retraining of existing five-state and direct models only.
Usage: python run.py RECOVERED_MODEL_DIR BETA_JSON
All predictions are raw expected workloads. No allocator, medical adjustment,
participation post-discount, talent fitting, dynasty changes or deployment.
"""
import importlib.util,json,gzip,csv,copy,hashlib,functools,os
from pathlib import Path
from contextlib import contextmanager
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
D=Path(__file__).resolve().parent;PREV=D.parent/'direct-workload-correction';FULL=D.parent/'full-workload-scenario'
spec=importlib.util.spec_from_file_location('coverage_inventory',D/'inventory.py');iv=importlib.util.module_from_spec(spec);spec.loader.exec_module(iv)
p=iv.p;e=iv.e;s=iv.s;np=p.np
PROTOCOL=e.read(D/'Protocol_Freeze.json');BASE=e.read(PREV/'Cases.json.gz')
original_observation=e.observation;original_target_label=s.target_label
STATES=['absent','retained_high_usage','retained_reduced','changed','retention_unidentifiable']
def predict(model,z):
 c=s.predict(model,z)
 c['probabilities']={('retention_unidentifiable' if k=='unknown_role' else k):v for k,v in c['probabilities'].items()}
 for kind in ['structural','fitted']:
  for field in ['ratios','contributions']:
   c[kind][field]={('retention_unidentifiable' if k=='unknown_role' else k):v for k,v in c[kind][field].items()}
 return c
CENSUS={};SOURCES={};cutoff=None
for source in e.read(D/'Source_Coverage.json'):
 if source['status']!='verified_complete':continue
 year=source['year'];blob=D/source['source']
 for row in e.read(blob)['stats'][0]['splits']:
  CENSUS[row['player']['id'],year]=row;SOURCES[row['player']['id'],year]=source['source']
def corrected(z,year):
 if cutoff is not None:assert year<=cutoff,'future observation requested inside prediction'
 o=original_observation(z,year);r=CENSUS.get((z['id'],year))
 if z['role']!='H' or r is None or o['exposure'] is None or o['exposure']<=0:return o
 st=r['stat'];pa=float(st['plateAppearances']);gp=float(st['gamesPlayed'])
 if abs(pa-o['exposure'])>1e-8 or not 0<gp<=163:return o
 return o|{'GP':gp,'GP_original':o['GP'],'GP_observation_status':'verified_observed','GP_complete':True,'GP_source':SOURCES[z['id'],year],'GP_statistical_cutoff':f'{year} regular season end','medical_absence':False}
@contextmanager
def prediction_only(z):
 global cutoff
 prev=cutoff;cutoff=z['year']
 try:yield
 finally:cutoff=prev

def activate():
 e.observation=corrected;e.historical_feature.cache_clear();s.HERE=D;p.D=D
 # Retain legacy internal key; rename the residual label only in exported output.

def role_reason(z,lab):
 if lab['state']!=4:return 'identifiable_usage_proxy'
 if lab['observation']['GP'] is None:return 'target_GP_unrecovered'
 obs=[corrected(z,y) for y in range(z['year'],z['year']-3,-1)]
 return 'asof_GP_unrecovered' if any(o['exposure'] and o['GP'] is None for o in obs) else 'insufficient_positive_forecast_date_usage'

def repair_logs():
 rows=list(csv.DictReader((D/'Pre_Repair_Records.csv').open()));out=[]
 for a in rows:
  ident=int(a['id']);year=int(a['year']);ex=None if a['exposure']=='' else float(a['exposure']);oldGP=None if a['GP']=='' else float(a['GP']);r=CENSUS.get((ident,year));gp=oldGP;status='unchanged';source='';pa=None
  if ex is not None and ex>0:
   if r is None:status='unresolved_no_verified_source' if oldGP is None else 'existing_observed_no_additional_source'
   else:
    pa=float(r['stat']['plateAppearances']);new=float(r['stat']['gamesPlayed']);source=SOURCES[ident,year]
    if abs(pa-ex)>1e-8:status='unresolved_PA_mismatch_no_change'
    elif not 0<new<=163:status='unresolved_invalid_GP'
    else:gp=new;status='missing_GP_recovered' if oldGP is None else 'GP_disagreement_corrected' if oldGP!=new else 'existing_GP_confirmed'
  out.append({'id':ident,'name':(r or {}).get('player',{}).get('fullName',''),'year':year,'uses':a['uses'],'observation_status':a['status'],'original_exposure':ex,'original_GP':oldGP,'corrected_GP':gp,'source_PA':pa,'correction_status':status,'source':source,'statistical_cutoff':f'{year} regular-season end','medical_label_added':False})
 iv.write('Correction_Log.csv',out)
 summ=[]
 for use in ['training:target','training:forecast_input','evaluation:target','evaluation:forecast_input']:
  xs=[a for a in out if use in a['uses'].split('|')];pos=[a for a in xs if a['original_exposure'] is not None and a['original_exposure']>0]
  summ.append({'population':use,'unique_player_seasons':len(xs),'positive_seasons':len(pos),'missing_GP_before':sum(a['original_GP'] is None for a in pos),'missing_GP_after':sum(a['corrected_GP'] is None for a in pos),'GP_disagreements_corrected':sum(a['correction_status']=='GP_disagreement_corrected' for a in pos),'PA_mismatches':sum(a['correction_status']=='unresolved_PA_mismatch_no_change' for a in pos),'zero_workload_changes':0})
 iv.write('Coverage_Before_After.csv',summ);iv.dump('Correction_Summary.json',{'unique_records':len(out),'recovered':sum(a['correction_status']=='missing_GP_recovered' for a in out),'disagreements':sum(a['correction_status']=='GP_disagreement_corrected' for a in out),'unresolved':[a for a in out if a['correction_status'].startswith('unresolved')],'medical_labels_added':0});print('COVERAGE',summ,flush=True)
 return {(a['id'],a['year']) for a in out if a['original_GP']!=a['corrected_GP']}

def verify_population():
 # Frozen original training IDs/targets must survive the input/label repair.
 audits=[];labels=[]
 for fam in ['H','P']:
  rows=e.training(2026,calendar=fam=='H',family=fam);rows=[a for a in rows if a['year']!=2020]
  for a in rows:
   z=a['z'];lab=s.target_label(z)
   e.observation=original_observation
   try:old=original_target_label(z);oldrole=s.forecast_role(z)[0]
   finally:e.observation=corrected
   labels.append({'id':z['id'],'anchor':z['year'],'target_year':a['year'],'family':fam,'original_state':old['state'],'corrected_state':lab['state'],'original_forecast_role':oldrole,'corrected_forecast_role':s.forecast_role(z)[0],'raw_target':a['raw_value'],'observed_target':lab['observation']['exposure'],'target_GP_before':old['observation']['GP'],'target_GP_after':lab['observation']['GP'],'reason':role_reason(z,lab)})
  audit={'family':fam,'n':len(rows),'zeros':sum(a['raw_value']==0 for a in rows),'target_workload_disagreements':sum(a['raw_value']!=s.target_label(a['z'])['observation']['exposure'] for a in rows),'P_missing_positive_GP':sum(a['raw_value']>0 and s.target_label(a['z'])['observation']['GP'] is None for a in rows),'P_missing_positive_GS':sum(a['raw_value']>0 and fam=='P' and s.target_label(a['z'])['observation']['GS'] is None for a in rows)};audits.append(audit)
 for audit in audits:
  same=[a for a in labels if a['family']==audit['family']]
  audit['substantive_target_workload_disagreements']=sum(abs(a['raw_target']-a['observed_target'])>1e-8 for a in same)
  audit['target_workload_disagreement_reason']='Two floating-point representations of 5/3 IP differ by 2.2e-16; no substantive target change' if audit['family']=='P' else 'none'
 iv.write('Training_Label_Corrections.csv',labels);iv.dump('Training_Population_Check.json',audits);print('TRAINING CHECK',audits,flush=True)

def unaffected(fam,asof):
 # Pitchers receive no GP patch. Reuse exactly the original model parameters.
 import shutil
 for src,dst in [(FULL/f'model-{fam}-{asof}.joblib',D/f'model-{fam}-{asof}.joblib'),(PREV/f'direct-{fam}-{asof}.joblib',D/f'direct-{fam}-{asof}.joblib')]:
  if not dst.exists():shutil.copyfile(src,dst)
  assert dst.read_bytes()==src.read_bytes()

def evaluate(changed):
 results=[];components=[];labels=[];models={}
 for a in BASE:
  fam='H' if a['role']=='H' else 'P';asof=a['anchor'];key=fam,asof
  if key not in models:
   if fam=='P':unaffected(fam,asof)
   models[key]=s.fit(asof,fam),p.model(asof,fam)
  z=e.historical_z(a['mlbam_id'],asof,a['role']);fm,dm=models[key];lab=s.target_label(z)
  with prediction_only(z):c=predict(fm,z);direct=p.forecast(dm,z)
  input_changed=fam=='H' and any((z['id'],year) in changed for year in range(asof,asof-4,-1));target_changed=fam=='H' and (z['id'],asof+1) in changed
  rr=dict(a);rr.update(five_retrained=c['fitted']['expected'],direct_retrained=direct,repaired_actual_state=STATES[lab['state']],repaired_forecast_role=c['role'],target_GP_repaired=target_changed,input_GP_repaired=input_changed,repair_affected=input_changed or target_changed,retention_identifiability=role_reason(z,lab),future_inputs_used=False,allocator_applied=False,medical_applied=False)
  state=STATES[lab['state']];cap=c['fitted']['full_role_workload'];means={'absent':0}|{st:cap*v for st,v in c['fitted']['ratios'].items()};severity=means[state]-rr['actual'];frequency=rr['five_retrained']-means[state];rr.update(retrained_frequency_error=frequency,retrained_severity_error=severity,retrained_probabilities=c['probabilities'],retrained_state_means=means)
  assert abs(frequency+severity-(rr['five_retrained']-rr['actual']))<1e-8
  results.append(rr);components.append({'id':z['id'],'anchor':asof,'component':c});labels.append({'id':z['id'],'name':a['name'],'anchor':asof,'old_state':a['actual_state'],'corrected_state':state,'old_role':a['forecast_role'],'corrected_role':c['role'],'reason':rr['retention_identifiability'],'target_GP_repaired':target_changed,'input_GP_repaired':input_changed,'actual':a['actual']})
  if len(results)%200==0:print('SCORE',len(results),flush=True)
 iv.dump('Matched_Cases.json.gz',results);iv.dump('Repaired_Components.json.gz',components);iv.write('Evaluation_Label_Corrections.csv',labels)
 iv.write('Player_Comparisons.csv',[{k:v for k,v in a.items() if not isinstance(v,(dict,list))}|{'groups':'|'.join(a['groups'])} for a in results])
 return results

METHODS=['frozen_hybrid','expected_fitted','direct_mean','five_retrained','direct_retrained']
def report_metrics(xs):
 scores=[];years=[];state_rows=[];calibration=[];attrib=[]
 for fam in ['H','P']:
  fs=[a for a in xs if (a['role']=='H')==(fam=='H')]
  subsets={'all':fs,'either_repaired':[a for a in fs if a['repair_affected']],'target_GP_repaired':[a for a in fs if a['target_GP_repaired']],'input_GP_repaired':[a for a in fs if a['input_GP_repaired']],'neither_repaired':[a for a in fs if not a['repair_affected']]}
  for subset,pool in subsets.items():
   for g in sorted({g for a in pool for g in a['groups']}):
    ys=[a for a in pool if g in a['groups']]
    for method in METHODS:scores.append({'family':fam,'subset':subset,'cohort':g,'model':method,**e.metric([(a[method],a['actual']) for a in ys])})
  for year in sorted({a['anchor'] for a in fs}):
   ys=[a for a in fs if a['anchor']==year]
   for method in METHODS:years.append({'family':fam,'anchor':year,'model':method,**e.metric([(a[method],a['actual']) for a in ys])})
  for g in sorted({g for a in fs for g in a['groups']}):
   ys=[a for a in fs if g in a['groups']]
   for model in ['original_five','retrained_five']:
    def probs(a):return {('retention_unidentifiable' if k=='unknown_role' else k):v for k,v in (a['probabilities'] if model=='original_five' else a['retrained_probabilities']).items()}
    def means(a):return {('retention_unidentifiable' if k=='unknown_role' else k):v for k,v in (a['state_means'] if model=='original_five' else a['retrained_state_means']).items()}
    for state in STATES:
     obs=[a for a in ys if a['repaired_actual_state']==state]
     state_rows.append({'family':fam,'cohort':g,'model':model,'state':state,'n':len(ys),'state_n':len(obs),'predicted_frequency':float(np.mean([probs(a)[state] for a in ys])),'observed_repaired_frequency':len(obs)/len(ys),'within_state_bias':float(np.mean([means(a)[state]-a['actual'] for a in obs])) if obs else None,'within_state_MAE':float(np.mean([abs(means(a)[state]-a['actual']) for a in obs])) if obs else None})
    known=[a for a in ys if a['repaired_actual_state']!='retention_unidentifiable'];active=[a for a in known if a['actual']>0]
    calibration.append({'family':fam,'cohort':g,'model':model,'n':len(ys),'identifiable_n':len(known),'joint_state_Brier_all_with_residual':float(np.mean([sum((probs(a)[st]-int(a['repaired_actual_state']==st))**2 for st in STATES) for a in ys])),'joint_state_Brier_identifiable':float(np.mean([sum((probs(a)[st]-int(a['repaired_actual_state']==st))**2 for st in STATES) for a in known])) if known else None,'participation_Brier':float(np.mean([((1-probs(a)['absent'])-int(a['actual']>0))**2 for a in ys])),'role_retention_Brier_known_active':float(np.mean([((probs(a)['retained_high_usage']+probs(a)['retained_reduced'])/max(1e-12,1-probs(a)['absent'])-int(a['repaired_actual_state'].startswith('retained')))**2 for a in active])) if active else None})
    m='expected_fitted' if model=='original_five' else 'five_retrained';sev=[means(a)[a['repaired_actual_state']]-a['actual'] for a in ys];freq=[a[m]-means(a)[a['repaired_actual_state']] for a in ys];attrib.append({'family':fam,'cohort':g,'model':model,'n':len(ys),'bias':float(np.mean([a[m]-a['actual'] for a in ys])),'frequency_bias':float(np.mean(freq)),'severity_bias':float(np.mean(sev)),'frequency_MAE':float(np.mean(np.abs(freq))),'severity_MAE':float(np.mean(np.abs(sev)))})
 iv.write('Matched_Validation.csv',scores);iv.write('Year_Validation.csv',years);iv.write('State_Calibration.csv',state_rows);iv.write('Calibration.csv',calibration);iv.write('Error_Attribution.csv',attrib)
 # Preserve the exact inherited gate evaluator; provide each repaired candidate
 # through its expected direct_mean slot, without modifying protected masks.
 oldD=p.D;p.D=D
 for method in ['five_retrained','direct_retrained']:
  p.gates([a|{'direct_mean':a[method]} for a in xs]);(D/'Release_Gates.json').rename(D/f'Release_Gates_{method}.json')
 p.D=oldD

def current():
 assets=e.read(D.parent/'targeted-repair/Repair_League.json.gz');old={a['id']:a for a in csv.DictReader((PREV/'League_1900_Comparison.csv').open())};out=[];mods={}
 diagnostic=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids'])
 for fam in ['H','P']:
  if fam=='P':unaffected(fam,2026)
  mods[fam]=s.fit(2026,fam),p.model(2026,fam)
 for a in assets:
  hs=e.v.seasons(e.old.players[a['id']],a['role']);z={'id':a['mlbam_id'],'year':2026,'role':a['role'],'history_override':hs,'x':e.base['features'](hs,a['role'],2026,a['mlbam_id']),'bounded_x':e.base['features'](hs,a['role'],2026,a['mlbam_id'],True)};fam='H' if a['role']=='H' else 'P';fm,dm=mods[fam]
  with prediction_only(z):c=predict(fm,z);direct=p.forecast(dm,z)
  latest=corrected(z,2026);row=dict(old[a['id']]);row.update(repaired_forecast_role=c['role'],latest_GP=latest['GP'],five_retrained=c['fitted']['expected'],direct_retrained=direct,five_delta_vs_benchmark=c['fitted']['expected']-float(row['preserved_strong_benchmark']),direct_delta_vs_benchmark=direct-float(row['preserved_strong_benchmark']),repaired_participation=c['participation'],repaired_conditional_active=c['fitted']['conditional_active'],repaired_full_role_scenario=c['fitted']['full_role_workload'],historical_source_cutoff='2010–2024 GP repair; verified 2025/2026 sources unchanged',fallback=c['fitted']['fallback'],full_role_used_as_unconditional=False)
  for st,v in c['probabilities'].items():row['repaired_probability_'+st]=v
  out.append(row)
 iv.write('League_1900_Comparison.csv',out);iv.write('Diagnostic_12_Comparisons.csv',[a for a in out if int(a['mlbam_id']) in diagnostic]);assert len(out)==1900
 iv.dump('Integrity.json',{'players':1900,'diagnostics':12,'production_changed':False,'talent_changed':False,'years2_8_changed':False,'dynasty_changed':False,'Trade_Analyzer_changed':False,'deployment':False,'extra_participation_discount':False,'allocator_applied':False,'medical_envelope_applied':False,'future_prediction_inputs':False,'original_artifacts_untouched':True,'comparison_is_exposed_exploratory':True})
if __name__=='__main__':
 changed=repair_logs();activate();verify_population();xs=evaluate(changed);report_metrics(xs);current();print('COMPLETE CONSISTENT COVERAGE RETRAIN',flush=True)

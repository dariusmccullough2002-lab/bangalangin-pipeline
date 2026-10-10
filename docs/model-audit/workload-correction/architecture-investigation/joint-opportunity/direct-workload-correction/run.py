"""Fixed research comparison. No deployment, collection-driven fitting or tuning."""
import os,sys,json,gzip,csv,hashlib,importlib.util,datetime,urllib.request
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
D=Path(__file__).resolve().parent;S=D.parent/'full-workload-scenario'
sys.path.insert(0,str(S));spec=importlib.util.spec_from_file_location('preserved_full_scenario',S/'run.py');scenario=importlib.util.module_from_spec(spec);spec.loader.exec_module(scenario)
e=scenario.e
PROTOCOL=json.loads((D/'Protocol_Freeze.json').read_text())
def put(name,a):
 b=json.dumps(a,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x).encode();(D/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def csvout(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
def features(z):
 f,d=e.evidence_features(z);rr,_=scenario.forecast_role(z)
 indices=list(range(15))+([17,18] if z['role']!='H' else [])
 return np.r_[f[indices],[rr==r for r in scenario.ROLES],[o['exposure'] is None for o in d['observations']]]
def model(asof,fam):
 p=D/f'direct-{fam}-{asof}.joblib'
 if p.exists():return joblib.load(p)
 rows=[a for a in e.training(asof,calendar=fam=='H',family=fam) if a['z']['id']%5 in [1,2,3] and a['year']!=2020]
 X=np.stack([features(a['z']) for a in rows]);y=np.array([a['raw_value'] for a in rows]);reg=HistGradientBoostingRegressor(loss='squared_error',**e.settings).fit(X,y,sample_weight=np.array([a['weight'] for a in rows]))
 out={'reg':reg,'manifest':{'asof':asof,'family':fam,'rows':len(rows),'zeros':int((y==0).sum()),'max_target':max(a['year'] for a in rows),'feature_count':X.shape[1],'target_sha256':hashlib.sha256(y.tobytes()).hexdigest(),'protocol_sha256':hashlib.sha256((D/'Protocol_Freeze.json').read_bytes()).hexdigest(),'unconditional_mean':True,'availability_multiplier':False}}
 assert out['manifest']['max_target']<=min(asof,2025);e.legacy.prior.checkpoint(out,p);print('FIT',fam,asof,len(rows),flush=True);return out
def forecast(m,z):return float(np.clip(m['reg'].predict(features(z)[None,:])[0],0,754 if z['role']=='H' else 251))
def fetch(tag,url):
 p=D/'verified'/f'{tag}.json.gz';p.parent.mkdir(exist_ok=True)
 if p.exists():return json.loads(gzip.decompress(p.read_bytes()))
 try:
  with urllib.request.urlopen(url,timeout=15) as response:b=response.read();http=response.headers.get('Date')
  a=json.loads(b);p.write_bytes(gzip.compress(b,mtime=0));(p.parent/f'{tag}.provenance.json').write_text(json.dumps({'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_date':http,'sha256':hashlib.sha256(b).hexdigest(),'retrospective_labels_only':True,'published_timestamp_unknown':True},indent=2));return a
 except Exception as exc:
  return {'fetch_error':str(exc),'url':url}
def bounded_evidence(cases):
 GP={};coverage=[]
 for year in [2018,2024]:
  a=fetch(f'GP{year}',f'https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={year}&sportIds=1&gameType=R&playerPool=ALL&limit=5000')
  if 'fetch_error' in a:coverage.append({'kind':'GP_census','year':year,'status':'unavailable',**a});continue
  splits=a['stats'][0]['splits'];assert len(splits)==a['stats'][0]['totalSplits']<5000
  for r in splits:GP[r['player']['id'],year]={'GP':float(r['stat']['gamesPlayed']),'PA':float(r['stat']['plateAppearances'])}
  coverage.append({'kind':'GP_census','year':year,'status':'fetched','rows':len(splits),'future_input':False})
 excluded=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);chosen={}
 for group in ['established','young','interrupted','aging33plus','uncertain_role']:
  rows=[a for a in cases if a['anchor']==2024 and group in a['groups'] and a['mlbam_id'] not in excluded]
  rows=sorted(rows,key=lambda a:hashlib.sha256(f"{a['mlbam_id']}:{a['anchor']}".encode()).hexdigest())[:6]
  for a in rows:chosen.setdefault(a['mlbam_id'],{'id':a['mlbam_id'],'name':a['name'],'cohorts':[]})['cohorts'].append(group)
 if (D/'Evidence_Sample_Freeze.json').exists():
  chosen={a['id']:a for a in e.read(D/'Evidence_Sample_Freeze.json')}
 else:put('Evidence_Sample_Freeze.json',list(chosen.values()))
 for ident,r in chosen.items():
  a=fetch(f'transactions-{ident}-2025',f'https://statsapi.mlb.com/api/v1/transactions?playerId={ident}&startDate=2025-01-01&endDate=2025-12-31')
  if 'fetch_error' in a:coverage.append({'kind':'transactions','id':ident,'status':'unavailable',**a});continue
  ts=a.get('transactions',[]);foreign=[t for t in ts if t.get('person',{}).get('id')!=ident]
  if foreign:coverage.append({'kind':'transactions','id':ident,'status':'query_filter_not_verified','response_rows':len(ts)});continue
  types=Counter(t.get('typeCode','unknown') for t in ts)
  coverage.append({'kind':'transactions','id':ident,'name':r['name'],'status':'dated_events_only' if ts else 'empty_not_health_evidence','rows':len(ts),'cohorts':'|'.join(r['cohorts']),'types':json.dumps(types),'coverage_complete':False,'absence_days_identifiable':False})
 csvout('Bounded_Evidence_Coverage.csv',coverage);return GP
from collections import Counter
def evaluate():
 old=e.read(S/'Chronological_Cases.json.gz');xs=[]
 for a in old:
  z=e.historical_z(a['mlbam_id'],a['anchor'],a['role']);fam='H' if a['role']=='H' else 'P';direct=forecast(model(a['anchor'],fam),z);c=a['component'];p=c['probabilities'];cap=c['fitted']['full_role_workload'];m={'absent':0}|{st:cap*ratio for st,ratio in c['fitted']['ratios'].items()};state=a['actual_state'];severity=m[state]-a['actual'];frequency=sum((p[s]-int(state==s))*m[s] for s in scenario.STATES)
  assert abs(frequency+severity-(a['expected_fitted']-a['actual']))<1e-7
  row={k:a[k] for k in ['mlbam_id','name','anchor','target_season','role','actual','actual_state','target_role','forecast_role','frozen_hybrid','strong_prior','repair','expected_fitted','actual_active']}
  cohort=e.cohort_key(z);analysis_groups=['all',z['role'],scenario.forecast_role(z)[0],cohort]
  if z['x'][13]>=33:analysis_groups.append('aging33plus')
  if scenario.forecast_role(z)[0]=='uncertain' or cohort in ['unstable','unknown']:analysis_groups.append('uncertain_role')
  row.update(groups=list(dict.fromkeys(analysis_groups)),protected_groups=a['groups'],direct_mean=direct,frequency_error=frequency,severity_error=severity,oracle_observed_state=m[state],state_means=m,probabilities=p)
  for s in scenario.STATES:row['frequency_'+s]=(p[s]-int(state==s))*m[s]
  o=scenario.target_label(z)['observation'];row.update(target_GP_missing=o['exposure']>0 and o['GP'] is None,target_GS_missing=o['exposure']>0 and a['role']!='H' and o['GS'] is None,asof_role_unidentified=a['forecast_role']=='uncertain')
  row['unknown_role_reason']='future_role_unobserved_due_GP_coverage' if state=='unknown_role' and row['target_GP_missing'] else 'retention_unidentifiable_due_asof_role' if state=='unknown_role' and row['asof_role_unidentified'] else 'not_unknown'
  xs.append(row)
  if len(xs)%300==0:print('COMPARE',len(xs),flush=True)
 put('Cases.json.gz',xs);csvout('Player_Comparisons.csv',[{k:v for k,v in a.items() if k not in {'groups','protected_groups','state_means','probabilities'}}|{'groups':'|'.join(a['groups']),'protected_groups':'|'.join(a['protected_groups'])} for a in xs])
 scores=[];attributions=[];states=[]
 methods=['frozen_hybrid','strong_prior','repair','expected_fitted','direct_mean']
 for window in ['all_exposed','pre2026_exposed','2026_exposed']:
  pool=[a for a in xs if window=='all_exposed' or (a['target_season']==2026)==(window=='2026_exposed')]
  for fam in ['H','P']:
   fs=[a for a in pool if (a['role']=='H')==(fam=='H')]
   for group in sorted({g for a in fs for g in a['groups']}):
    ys=[a for a in fs if group in a['groups']]
    for method in methods:scores.append({'window':window,'family':fam,'cohort':group,'model':method,**e.metric([(a[method],a['actual']) for a in ys])})
    attributions.append({'window':window,'family':fam,'cohort':group,'n':len(ys),'outcome_bias':float(np.mean([a['expected_fitted']-a['actual'] for a in ys])),'frequency_bias':float(np.mean([a['frequency_error'] for a in ys])),'severity_bias':float(np.mean([a['severity_error'] for a in ys])),'frequency_MAE':float(np.mean([abs(a['frequency_error']) for a in ys])),'severity_MAE':float(np.mean([abs(a['severity_error']) for a in ys])),'oracle_state_MAE':e.metric([(a['oracle_observed_state'],a['actual']) for a in ys])['MAE'],'unknown_due_target_GP_missing':sum(a['actual_state']=='unknown_role' and a['target_GP_missing'] for a in ys),'unknown_due_asof_role_unidentified':sum(a['actual_state']=='unknown_role' and a['asof_role_unidentified'] for a in ys)})
    for s in scenario.STATES:
     obs=[a for a in ys if a['actual_state']==s];states.append({'window':window,'family':fam,'cohort':group,'state':s,'n':len(ys),'state_n':len(obs),'predicted_frequency':float(np.mean([a['probabilities'][s] for a in ys])),'observed_frequency':len(obs)/len(ys),'conditional_severity_bias':float(np.mean([a['state_means'][s]-a['actual'] for a in obs])) if obs else None,'frequency_error_contribution':float(np.mean([a['frequency_'+s] for a in ys]))})
 csvout('Chronological_Validation.csv',scores);csvout('Error_Attribution.csv',attributions);csvout('State_Frequency_Severity.csv',states)
 csvout('Year_Validation.csv',[{'anchor':year,'family':fam,'model':m,**e.metric([(a[m],a['actual']) for a in xs if a['anchor']==year and (a['role']=='H')==(fam=='H')])} for year in sorted({a['anchor'] for a in xs}) for fam in ['H','P'] for m in methods])
 GP=bounded_evidence(xs);corrections=[]
 for a in xs:
  if a['role']!='H' or not a['target_GP_missing'] or (a['mlbam_id'],a['target_season']) not in GP:continue
  new=GP[a['mlbam_id'],a['target_season']]
  if abs(new['PA']-a['actual'])>1e-8:corrections.append({'id':a['mlbam_id'],'target_season':a['target_season'],'status':'PA_mismatch_no_label_change'});continue
  z=e.historical_z(a['mlbam_id'],a['anchor'],'H');o=scenario.target_label(z)['observation']|{'GP':new['GP']};role=scenario.role_from(o,'H');fr=a['forecast_role'];state='unknown_role' if fr=='uncertain' else 'changed' if role!=fr else 'retained_high_usage' if scenario.full_proxy(o,role,a['target_season']) else 'retained_reduced';mm=a['state_means'][state];corrections.append({'id':a['mlbam_id'],'name':a['name'],'target_season':a['target_season'],'status':'target_GP_verified','old_state':a['actual_state'],'corrected_target_role':role,'corrected_state':state,'GP':new['GP'],'before_frequency_error':a['frequency_error'],'after_frequency_error':a['expected_fitted']-mm,'before_severity_error':a['severity_error'],'after_severity_error':mm-a['actual'],'numerical_forecast_change':0,'before_oracle_error':a['oracle_observed_state']-a['actual'],'after_oracle_error':mm-a['actual']})
 csvout('Coverage_Label_Correction.csv',corrections);gates(xs);return xs
def gates(xs):
 source=e.read(S/'Release_Gates.json');out=[]
 original={(a['mlbam_id'],a['anchor']) for a in e.read(D.parent.parent.parent/'Historical_Cases.json')};expanded={(a['mlbam_id'],a['anchor'],a['role']) for a in e.read(D.parent/'first-year-repair/P_Cases.json.gz')[:1084]};ret=[a for a in xs if a['target_season']!=2026]
 pools={'original94':[a for a in ret if a['role']!='H' and (a['mlbam_id'],a['anchor']) in original],'expandedP':[a for a in ret if (a['mlbam_id'],a['anchor'],a['role']) in expanded],'H_standard':[a for a in ret if a['role']=='H']}
 pools.update(originalSP=[a for a in pools['original94'] if a['role']=='SP'],additional_expandedSP=[a for a in pools['expandedP'] if a['role']=='SP'],additional_youngSP=[a for a in pools['expandedP'] if 'young_SP' in a['protected_groups'] and a['role']=='SP'],additional_stableSP_vs_strong=[a for a in pools['expandedP'] if 'stable_rotation' in a['protected_groups']],additional_durableH_vs_strong=[a for a in pools['H_standard'] if 'durable_four_years' in a['protected_groups']])
 hidx={(a['mlbam_id'],a['anchor']):a for a in e.read(D.parent/'roster-opportunity/Integrated_H_Cases.json.gz')}
 for g in source['gates']:
  if g.get('method')!='expected_fitted':continue
  name=g['gate']
  if name in pools:
   ys=pools[name];v=e.metric([(a['direct_mean'],a['actual']) for a in ys])['MAE'];out.append({'gate':name,'n':len(ys),'value':v,'limit':g['limit'],'pass':v<=g['limit']})
  elif name=='comparable_high_RBI_bias':
   ys=[a for a in ret if 'high_RBI_comparable62' in a['protected_groups']];err=[]
   for a in ys:
    old=hidx[a['mlbam_id'],a['anchor']];b=old['baseline'];err.append(b['RBI']*a['direct_mean']/b['PA']-old['actual'].get('RBI',0))
   v=float(np.mean(err));out.append({'gate':name,'n':len(ys),'value':v,'limit':3,'pass':abs(v)<=3})
  elif 'anchor_' in name:
   year=int(name.split('_')[-2]);ys=[a for a in (pools['expandedP'] if '_P_' in name else pools['H_standard']) if a['anchor']==year];by={}
   for a in ys:by.setdefault(a['mlbam_id'],[]).append(abs(a['direct_mean']-a['actual'])-abs(a['strong_prior']-a['actual']))
   ar=list(by.values());n=np.array([len(v) for v in ar]);s=np.array([sum(v) for v in ar]);rng=np.random.default_rng(2718);ix=rng.integers(0,len(ar),(1500,len(ar)));ci=np.quantile(s[ix].sum(1)/n[ix].sum(1),[.025,.975]).tolist();old=e.metric([(a['strong_prior'],a['actual']) for a in ys])['MAE'];v=e.metric([(a['direct_mean'],a['actual']) for a in ys])['MAE'];out.append({'gate':name,'n':len(ys),'value':v,'prior':old,'paired95':ci,'pass':not(v>1.1*old and ci[0]>0)})
 out.extend([{'gate':'independent_untouched_confirmation','pass':False},{'gate':'matched_historical_allocator_accuracy','pass':False},{'gate':'clinical_absence_intervals_identified','pass':False}]);put('Release_Gates.json',{'gates':out,'all_gates_pass':all(a['pass'] for a in out),'numerical_promotion':False,'prior_gates_preserved':True})
def current():
 assets=e.read(D.parent/'targeted-repair/Repair_League.json.gz');sc={a['id']:a for a in csv.DictReader((S/'League_1900_Comparison.csv').open())};out=[];ids=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);models={fam:model(2026,fam) for fam in ['H','P']}
 for a in assets:
  hs=e.v.seasons(e.old.players[a['id']],a['role']);z={'id':a['mlbam_id'],'year':2026,'role':a['role'],'history_override':hs,'x':e.base['features'](hs,a['role'],2026,a['mlbam_id']),'bounded_x':e.base['features'](hs,a['role'],2026,a['mlbam_id'],True)};key='PA' if a['role']=='H' else 'IP';s=sc[a['id']];v=forecast(models['H' if a['role']=='H' else 'P'],z);o=e.observation(z,2026)
  out.append({'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':a['role'],'forecast_role':scenario.forecast_role(z)[0],'latest_verified_workload':o['exposure'],'observation_status':o['status'],'latest_GP':o['GP'],'latest_GS':o['GS'],'production':a['production'][key],'preserved_strong_benchmark':a['frozen_hybrid'][key],'five_state_raw_expected':float(s['raw_expected_before_count_adapter']),'direct_unconditional_mean':v,'direct_delta_vs_benchmark':v-a['frozen_hybrid'][key],'full_role_separate_scenario':float(s['full_role_PA_IP']),'prior_allocator_sensitivity':float(s['team_allocation_adjustment']),'prior_medical_sensitivity':float(s['medical_envelope_adjustment']),'direct_participation_multiplier':1,'allocator_applied':False,'medical_envelope_applied':False,'years2_8_changed':False,'source_date':o['source_date'],'uncertainty':'unconditional point mean; no independent promotion evidence'})
 csvout('League_1900_Comparison.csv',out);csvout('Diagnostic_12_Comparisons.csv',[a for a in out if a['mlbam_id'] in ids]);assert len(out)==1900
 put('Integrity.json',{'players':1900,'diagnostics':12,'no_extra_absence_multiplier':True,'production_changed':False,'dynasty_changed':False,'talent_changed':False,'prospect_changed':False,'deployment_authorized':False,'model_selection_from_exposed_data':False})
if __name__=='__main__':evaluate();current();print('COMPLETE bounded comparison',flush=True)

"""Two frozen probability-only corrections. Parent model artifacts stay immutable."""
import importlib.util,json,gzip,csv,copy,hashlib,os
from pathlib import Path
import numpy as np,joblib
from sklearn.linear_model import LogisticRegression
D=Path(__file__).resolve().parent;C=D.parent/'historical-coverage-retrain'
spec=importlib.util.spec_from_file_location('coverage_parent',C/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.activate();e=r.e;s=r.s;BASE=e.read(C/'Matched_Cases.json.gz');STATES=r.STATES

def put(name,a):
 b=json.dumps(a,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v).encode();(D/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
MODEL_CACHE={};BASE_CACHE={}
def base_model(asof,fam):
 key=asof,fam
 if key not in BASE_CACHE:BASE_CACHE[key]=joblib.load(C/f'model-{fam}-{asof}.joblib')
 return BASE_CACHE[key]
def calibrated(asof,fam):
 key=asof,fam
 if key in MODEL_CACHE:return MODEL_CACHE[key]
 base=base_model(asof,fam);path=D/f'cal-{fam}-{asof}.joblib'
 if path.exists():artifact=joblib.load(path)
 else:
  rows=[a for a in e.training(asof,calendar=fam=='H',family=fam) if a['year']!=2020 and a['z']['id']%5==4 and (fam=='H' or s.forecast_role(a['z'])[0]=='starter')];rows=[a for a in rows if s.target_label(a['z']) is not None]
  X=np.stack([s.inputs(a['z'])[0] for a in rows]);y=np.array([s.target_label(a['z'])['state'] for a in rows]);classes=base['classifier'].classes_;counts={int(c):int((y==c).sum()) for c in classes};unsupported=sorted(set(map(int,y))-set(map(int,classes)))
  cal=None;eligible=len(rows)>=100 and len(classes)>=2 and min(counts.values())>=10 and not unsupported
  if eligible:cal=LogisticRegression(C=1,max_iter=1000).fit(np.log(np.clip(base['classifier'].predict_proba(X),1e-6,1)),y,sample_weight=np.array([a['weight'] for a in rows]))
  artifact={'calibrator':cal,'manifest':{'asof':asof,'family':fam,'scope':'all hitters' if fam=='H' else 'demonstrated starters only','rows':len(rows),'IDmods':sorted({a['z']['id']%5 for a in rows}),'latest_target':max(a['year'] for a in rows),'classes':list(map(int,classes)),'support':counts,'unsupported_targets':unsupported,'applied':eligible,'fallback':'unchanged repaired uncalibrated probabilities' if not eligible else None,'base_sha256':hashlib.sha256((C/f'model-{fam}-{asof}.joblib').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((D/'Protocol_Freeze.json').read_bytes()).hexdigest()}}
  joblib.dump(artifact,path,compress=3);print('CAL',fam,asof,artifact['manifest'],flush=True)
 m=dict(base);m['calibrator']=artifact['calibrator'];MODEL_CACHE[key]=m,artifact;return m,artifact

def candidate(z):
 fam='H' if z['role']=='H' else 'P';m,a=calibrated(z['year'],fam)
 if fam=='P' and s.forecast_role(z)[0]!='starter':m=base_model(z['year'],'P')
 with r.prediction_only(z):return r.predict(m,z)

def evaluate():
 out=[];decomp=[];components=[]
 for a in BASE:
  z=e.historical_z(a['mlbam_id'],a['anchor'],a['role']);c=candidate(z);fam='H' if a['role']=='H' else 'P';new=c['fitted']['expected'];row=dict(a);row.update(calibrated_workload=new,H_calibration_alone=new if fam=='H' else a['five_retrained'],P_starter_calibration_alone=new if fam=='P' else a['five_retrained'],calibrated_probabilities=c['probabilities'],calibrated_conditional_active=c['fitted']['conditional_active'],calibrated_participation=c['participation'])
  means={'absent':0}|{k:c['fitted']['full_role_workload']*v for k,v in c['fitted']['ratios'].items()};old=a['retrained_state_means'];assert all(abs(means[k]-old[k])<1e-8 for k in STATES);delta=sum((c['probabilities'][k]-a['retrained_probabilities'][k])*old[k] for k in STATES);assert abs(delta-(new-a['five_retrained']))<1e-8
  row['probability_only_workload_delta']=delta;out.append(row);components.append({'id':z['id'],'anchor':z['year'],'component':c})
  decomp.append({'id':z['id'],'name':a['name'],'anchor':z['year'],'forecast_role':c['role'],'full_role_GS':c['fitted']['slots'].get('GS'),'full_role_IP_PA':c['fitted']['full_role_workload'],'before_given_active':a['five_retrained']/(1-a['retrained_probabilities']['absent']) if a['retrained_probabilities']['absent']<1 else 0,'after_given_active':c['fitted']['conditional_active'],'before_unconditional':a['five_retrained'],'after_unconditional':new,'before_participation':1-a['retrained_probabilities']['absent'],'after_participation':c['participation'],'benchmark':a['frozen_hybrid'],'direct':a['direct_retrained'],'actual':a['actual'],'observed_state':a['repaired_actual_state'],**{'mean_'+k:v for k,v in means.items()},**{'before_p_'+k:v for k,v in a['retrained_probabilities'].items()},**{'after_p_'+k:v for k,v in c['probabilities'].items()}})
  if len(out)%400==0:print('COMPARE',len(out),flush=True)
 put('Cases.json.gz',out);put('Components.json.gz',components);write('Chronological_Decomposition.csv',decomp);metrics(out);rbi(out);return out

def metrics(xs):
 scores=[];years=[];cal=[];bins=[];states=[]
 for fam in ['H','P']:
  fs=[a for a in xs if (a['role']=='H')==(fam=='H')]
  groups={g for a in fs for g in a['groups']}|{'demonstrated_starter','demonstrated_reliever','demonstrated_swingman'} if fam=='P' else {g for a in fs for g in a['groups']}
  for group in sorted(groups):
   ys=[a for a in fs if (a['repaired_forecast_role']==group.replace('demonstrated_','')) if group.startswith('demonstrated_')] if group.startswith('demonstrated_') else [a for a in fs if group in a['groups']]
   if not ys:continue
   for m in ['frozen_hybrid','five_retrained','direct_retrained','calibrated_workload']:scores.append({'family':fam,'cohort':group,'model':m,**e.metric([(a[m],a['actual']) for a in ys])})
   for model in ['repaired','calibrated']:
    key='retrained_probabilities' if model=='repaired' else 'calibrated_probabilities';cal.append({'family':fam,'cohort':group,'model':model,'n':len(ys),'joint_Brier':float(np.mean([sum((a[key][st]-int(a['repaired_actual_state']==st))**2 for st in STATES) for a in ys])),'participation_Brier':float(np.mean([((1-a[key]['absent'])-int(a['actual']>0))**2 for a in ys]))})
    for st in STATES:
     obs=[a for a in ys if a['repaired_actual_state']==st];states.append({'family':fam,'cohort':group,'model':model,'state':st,'n':len(ys),'state_n':len(obs),'predicted':float(np.mean([a[key][st] for a in ys])),'observed':len(obs)/len(ys),'fixed_within_state_bias':float(np.mean([a['retrained_state_means'][st]-a['actual'] for a in obs])) if obs else None})
     for b in range(10):
      bs=[a for a in ys if min(9,int(a[key][st]*10))==b]
      if bs:bins.append({'family':fam,'cohort':group,'model':model,'state':st,'bin':b,'n':len(bs),'predicted':float(np.mean([a[key][st] for a in bs])),'observed':float(np.mean([a['repaired_actual_state']==st for a in bs]))})
  for year in sorted({a['anchor'] for a in fs}):
   for m in ['frozen_hybrid','five_retrained','calibrated_workload']:years.append({'family':fam,'anchor':year,'model':m,**e.metric([(a[m],a['actual']) for a in fs if a['anchor']==year])})
 write('Validation.csv',scores);write('Year_Validation.csv',years);write('Calibration.csv',cal);write('Reliability_Bins.csv',bins);write('State_Frequencies.csv',states)
 # Two separate gate evaluations, with the other family unchanged.
 parentD=r.p.D;r.p.D=D
 for method in ['H_calibration_alone','P_starter_calibration_alone']:
  r.p.gates([a|{'direct_mean':a[method]} for a in xs]);(D/'Release_Gates.json').rename(D/f'Release_Gates_{method}.json')
 r.p.D=parentD

def rbi(xs):
 idx={(a['mlbam_id'],a['anchor']):a for a in e.read(D.parent/'roster-opportunity/Integrated_H_Cases.json.gz')};rows=[]
 for a in xs:
  if a['role']!='H' or a['target_season']==2026:continue
  original=idx[a['mlbam_id'],a['anchor']];b=original['baseline'];actualPA=original['actual'].get('PA',0);actualRBI=original['actual'].get('RBI',0);rate=b['RBI']/b['PA'] if b['PA'] else 0;anchor=e.lookup.get((a['mlbam_id'],a['anchor'],'H'),{}).get('stat',{});high='high_RBI_comparable62' in a['protected_groups'];assert not high or (anchor.get('PA',0)>=500 and anchor.get('RBI',0)>=90)
  for m in ['frozen_hybrid','five_retrained','calibrated_workload']:
   pred=rate*a[m];work=rate*(a[m]-actualPA);rateerr=rate*actualPA-actualRBI;reconciled=e.v.reconcile({k:v*a[m]/b['PA'] for k,v in b.items()})['RBI'];rows.append({'id':a['mlbam_id'],'name':a['name'],'anchor':a['anchor'],'high_RBI_gate':high,'model':m,'rate_RBI_per_PA':rate,'forecast_PA':a[m],'actual_PA_diagnostic_only':actualPA,'actual_RBI':actualRBI,'predicted_RBI':pred,'workload_error_contribution':work,'rate_error_at_actual_PA':rateerr,'total_error':pred-actualRBI,'reconciliation_RBI_delta':reconciled-pred,'anchor_PA':anchor.get('PA',0),'anchor_RBI':anchor.get('RBI',0)});assert abs(work+rateerr-(pred-actualRBI))<1e-8
 write('RBI_Player_Decomposition.csv',rows);summ=[]
 for high in [False,True]:
  for m in ['frozen_hybrid','five_retrained','calibrated_workload']:
   ys=[a for a in rows if a['model']==m and (not high or a['high_RBI_gate'])];summ.append({'population':'high_RBI_gate62' if high else 'all_retrospective_hitters','model':m,'n':len(ys),**{k:float(np.mean([a[k] for a in ys])) for k in ['total_error','workload_error_contribution','rate_error_at_actual_PA','reconciliation_RBI_delta']}})
 write('RBI_Attribution.csv',summ)

def current():
 before=list(csv.DictReader((C/'League_1900_Comparison.csv').open()));assets={a['id']:a for a in e.read(D.parent/'targeted-repair/Repair_League.json.gz')};diagnostic=set(e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);out=[]
 for a in before:
  asset=assets[a['id']];hs=e.v.seasons(e.old.players[a['id']],a['role']);z={'id':int(a['mlbam_id']),'year':2026,'role':a['role'],'history_override':hs,'x':e.base['features'](hs,a['role'],2026,int(a['mlbam_id'])),'bounded_x':e.base['features'](hs,a['role'],2026,int(a['mlbam_id']),True)};c=candidate(z);new=c['fitted']['expected'];a.update(H_calibration_workload=new if a['role']=='H' else float(a['five_retrained']),P_starter_calibration_workload=new if a['role']!='H' else float(a['five_retrained']),family_candidate_illustration_not_combined_forecast=new,calibrated_conditional_active=c['fitted']['conditional_active'],calibrated_participation=c['participation'],full_role_scenario=c['fitted']['full_role_workload'],scenario_not_valuation_input=True,combined_candidate_selected=False)
  for st,v in c['probabilities'].items():a['calibrated_p_'+st]=v
  out.append(a)
 write('League_1900_Comparison.csv',out);write('Diagnostic_12_Comparisons.csv',[a for a in out if int(a['mlbam_id']) in diagnostic]);assert len(out)==1900
 put('Integrity.json',{'players':1900,'diagnostics':12,'only_probability_calibration_changed':True,'classifier_and_severity_fixed':True,'no_synthetic_class_examples':True,'production_changed':False,'talent_rates_changed':False,'years2_8_changed':False,'dynasty_changed':False,'Trade_Analyzer_changed':False,'allocator_applied':False,'medical_applied':False,'deployment':False,'combined_candidate_selected':False})
if __name__=='__main__':evaluate();current();print('COMPLETE TWO FROZEN CALIBRATION TESTS',flush=True)

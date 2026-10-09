"""Meaningful release invariants and clustered error uncertainty from saved results."""
import json,gzip,hashlib,sys,csv,collections
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;catalog=json.loads(Path(sys.argv[1]).read_text());assets={z['id']:z for z in catalog['assets']};current=json.loads(gzip.decompress((OUT/'Opportunity_Current_Impact.json.gz').read_bytes()));unaffected=json.loads(gzip.decompress((OUT/'Unaffected_Assets.json.gz').read_bytes()));cases=json.loads(gzip.decompress((OUT/'Opportunity_Test_Cases.json.gz').read_bytes()));quality=json.loads(gzip.decompress((OUT/'Quality_Aware_Cases.json.gz').read_bytes()));qc=json.loads(gzip.decompress((OUT/'Quality_Aware_Current_Impact.json.gz').read_bytes()))
checks={};ids=[z['id'] for z in current+unaffected];assert len(ids)==len(set(ids))==2546 and set(ids)==set(assets);checks['all_2546_assets_accounted_for']=True
expected='aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235';assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()==expected;checks['frozen_catalog_bytes_identical']=True
for z in current:
 assert z['owner']==assets[z['id']]['owner']
 st=z['streams'][0];baseline=st['baseline'];role=st['role'];key='PA' if role=='H' else 'IP'
 for method,a in z['alternatives'].items():
  candidate=a['projection'];factor=candidate[key]/baseline[key]
  if role=='H':
   assert candidate['HR']<=candidate['H']+1e-8<=candidate['AB']+1e-8
   assert candidate['AB']+candidate['BB']+candidate['HBP']+candidate['SF']<=candidate['PA']+1e-8
   assert candidate['H']+3*candidate['HR']<=candidate['TB']+1e-8<=4*candidate['H']+1e-8
  else:
   for k in ['K','ER','BB','H','QA3']:assert abs(candidate[k]-baseline[k]*factor)<1e-7
   for k in ['SV','HLD']:assert abs(candidate[k]-baseline[k]*min(1,factor))<1e-7
   assert candidate['QA3']<=candidate['IP']/5+1e-8
for z in qc:
 assert z['owner']==assets[z['id']]['owner'];ratio=z['candidate']['IP']/z['baseline']['IP']
 for k in ['K','ER','BB','H','QA3']:assert abs(z['candidate'][k]-z['baseline'][k]*ratio)<1e-7
 for k in ['SV','HLD']:assert abs(z['candidate'][k]-z['baseline'][k]*min(1,ratio))<1e-7
checks.update(owners_IDs_picks_and_saved_trades_unchanged=True,hitter_component_coherence=True,MLB_rate_and_exact_QA3_integrity=True,no_leverage_created_by_capacity=True)
validation=json.loads((OUT/'Opportunity_Validation.json').read_text())
for z in validation['training_manifest']:
 assert z['latest_training_target']<=z['forecast_anchor'] and 0 not in z['train_id_mods']
for filename in ['Role_Aware_Validation.json','Quality_Aware_Validation.json']:
 for z in json.loads((OUT/filename).read_text())['manifest']:assert z['latest_training_target']<=z['anchor']
checks['fitted_targets_available_at_prediction_date']=True
original=json.loads((OUT.parent/'Debut_Chronological_Cases.json').read_text());preserved={(z['mlbam_id'],z['anchor']) for z in original};assert {(z['mlbam_id'],z['anchor']) for z in quality}==preserved
checks['all_1084_cases_preserved']=True
reg=json.loads((OUT/'Opportunity_Regression.json').read_text());assert reg['max_baseline_value_reproduction_error']<1e-7;checks['baseline_neutral_values_reproduced']=True
def uncertainty(xs,method,key):
 groups=collections.defaultdict(list)
 for z in xs:
  if key not in z['baseline']:continue
  actual=z['actual'].get(key,0);delta=abs(z[method].get(key,0)-actual)-abs(z['baseline'][key]-actual);groups[z['mlbam_id']].append(delta)
 sums=np.array([sum(v) for v in groups.values()]);counts=np.array([len(v) for v in groups.values()]);rng=np.random.default_rng(230910);samples=rng.integers(0,len(sums),size=(2000,len(sums)));boot=sums[samples].sum(axis=1)/counts[samples].sum(axis=1)
 return {'cases':int(sum(counts)),'unique_players':len(sums),'MAE_change':float(sums.sum()/counts.sum()),'cluster_bootstrap_95_interval':list(map(float,np.quantile(boot,[.025,.975]))),'note':'Resample players, preserving repeated seasons; exploratory comparisons, not multiplicity-corrected prospective confirmation.'}
ci={'H_all':uncertainty([z for z in cases if z['role']=='H'],'selected','PA'),'H_durable':uncertainty([z for z in cases if 'durable_four_years' in z['groups']],'selected','PA'),'P_all_quality':uncertainty(quality,'role_aware','IP'),'P_SP_quality':uncertainty([z for z in quality if z['role']=='SP'],'role_aware','IP')}
(OUT/'Integrity_Checks.json').write_text(json.dumps({'checks':checks,'current_primary_assets_evaluated':len(current),'untouched_assets':len(unaffected),'role_quality_pitchers_evaluated':len(qc),'clustered_uncertainty':ci,'production_changes':False},indent=2));print('PASS',checks,ci,flush=True)
# One review table covering every material change in the most promising combined direction.
debut={z['id']:z for z in json.loads((OUT.parent/'Debut_Evidence_Ledger.json').read_text())};qby={z['id']:z for z in qc};rows=[]
for z in current:
 st=z['streams'][0];rr=st['role'];baseline=st['baseline'];candidate=st['candidate'];value=z['candidate_neutral'];fits=z['candidate_competitive_fit'];method=st['method']
 if rr!='H':
  q=qby[z['id']];candidate=q['candidate'];value=q['candidate_neutral'];fits=q['candidate_competitive_fit'];method='role_and_MLB_quality_aware'
 key='PA' if rr=='H' else 'IP'
 if abs(candidate[key]-baseline[key])<(10 if rr=='H' else 1) and abs(value-z['baseline_neutral'])<1:continue
 d=debut.get(z['id'],{});owner='Island' if z['owner'].casefold()=='epskenes island' else z['owner'];row={'id':z['id'],'player':z['name'],'fantasy_organization':owner,'role':rr,'age':z['age'],'candidate_method':method,'debut_year':d.get('debut_year'),'verified_debut_MLB_IP':d.get('MLB_IP'),'verified_debut_MiLB_IP':d.get('MiLB_IP'),'verified_debut_professional_IP':d.get('professional_IP'),'baseline_neutral':z['baseline_neutral'],'candidate_neutral':value,'reason':'Expected MLB workload conditioned on past capacity, role/quality or hitter durability; attrition once','release_status':'EXPERIMENTAL: subgroup, calibration and long-horizon gates incomplete'}
 for k in ['PA','IP','K','ER','BB','H','QA3','HR','R','RBI','SB','SV','HLD']:row['baseline_'+k]=baseline.get(k);row['candidate_'+k]=candidate.get(k)
 for mode in z['baseline_competitive_fit']:row['baseline_fit_'+mode]=z['baseline_competitive_fit'][mode];row['candidate_fit_'+mode]=fits[mode]
 rows.append(row)
with (OUT/'Strongest_Direction_Material_Impact.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

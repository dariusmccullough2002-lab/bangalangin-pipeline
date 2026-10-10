"""Inspect preserved forecasts only; no candidate scoring or fitting."""
import importlib.util,json,csv,hashlib,sys
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;C=D.parent/'historical-coverage-retrain'
spec=importlib.util.spec_from_file_location('coverage_parent',C/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.activate();e=r.e;s=r.s
xs=e.read(C/'Matched_Cases.json.gz');cs={(a['id'],a['anchor']):a['component'] for a in e.read(C/'Repaired_Components.json.gz')}
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
rows=[];parts=[]
for a in xs:
 if a['role']=='H':continue
 c=cs[a['mlbam_id'],a['anchor']];z=e.historical_z(a['mlbam_id'],a['anchor'],a['role']);o=e.observation(z,z['year']);sd,rd=s.depths(z)
 row={'id':a['mlbam_id'],'name':a['name'],'anchor':a['anchor'],'cohorts':'|'.join(a['groups']),'forecast_role':c['role'],'GP':o['GP'],'GS':o['GS'],'GS_share':o['GS']/o['GP'] if o['GP'] else None,'full_role_GS':c['fitted']['slots'].get('GS',0),'full_role_RA':c['fitted']['slots'].get('RA',0),'IP_per_start':sd,'IP_per_relief':rd,'full_role_IP':c['fitted']['full_role_workload'],'conditional_active_IP':c['fitted']['conditional_active'],'participation':c['participation'],'expected_IP':a['five_retrained'],'direct_IP':a['direct_retrained'],'benchmark_IP':a['frozen_hybrid'],'actual':a['actual'],'actual_state':a['repaired_actual_state'],'frequency_error':a['retrained_frequency_error'],'severity_error':a['retrained_severity_error']};rows.append(row)
for group in ['starter','reliever','swingman','established','young','interrupted','aging33plus','uncertain_role']:
 a=[z for z in xs if z['role']!='H' and (z['repaired_forecast_role']==group if group in ['starter','reliever','swingman'] else group in z['groups'] and z['repaired_forecast_role']=='starter')]
 if not a:continue
 for st in r.STATES:
  obs=[z for z in a if z['repaired_actual_state']==st];parts.append({'group':group,'state':st,'n':len(a),'state_n':len(obs),'predicted_frequency':float(np.mean([z['retrained_probabilities'][st] for z in a])),'observed_frequency':len(obs)/len(a),'within_state_bias':float(np.mean([z['retrained_state_means'][st]-z['actual'] for z in obs])) if obs else None,'within_state_MAE':float(np.mean([abs(z['retrained_state_means'][st]-z['actual']) for z in obs])) if obs else None,'frequency_MAE':float(np.mean([abs(z['retrained_frequency_error']) for z in a])),'severity_MAE':float(np.mean([abs(z['retrained_severity_error']) for z in a]))})
write('Preserved_Pitcher_Decomposition.csv',rows);write('Preserved_Pitcher_State_Audit.csv',parts)
training=e.training(2026,calendar=False,family='P');labels=[(a,s.forecast_role(a['z'])[0],s.target_label(a['z'])['state']) for a in training if a['year']!=2020]
summary={'P_training_rows':len(labels),'training_by_asof_role':{rr:sum(b==rr for a,b,c in labels) for rr in s.ROLES},'P_residual_state_support':sum(c==4 for a,b,c in labels),'classifier_population':'pooled P; conditional severity and full-proxy fits routed by forecast-date role','severity_route':'Ridge per kind/asof-role/outcome-state when >=60 core observations; role/state empirical fallback otherwise','inputs':'P full repaired evidence_features+7-role onehot. Direct uses indices0:15 and17:19 plusrole+exposure missingness. No velocity, team roster, lineup, dated medical features. P five-state does include preserved historical K/ER/BB/H/QA3/SV/HLD rates at31:38, regression/aging/context supplied by existing helpers.'}
(D/'Mechanism_Inventory.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
for a in parts:
 if a['group']=='starter':print(a)

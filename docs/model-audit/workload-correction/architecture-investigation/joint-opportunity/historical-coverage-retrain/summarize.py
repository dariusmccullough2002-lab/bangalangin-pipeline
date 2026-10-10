"""Reproducible descriptive summaries of the fixed comparison; no fitting."""
from pathlib import Path
import csv,json,gzip,hashlib,collections
import numpy as np,joblib
D=Path(__file__).resolve().parent
xs=json.loads(gzip.decompress((D/'Matched_Cases.json.gz').read_bytes()))
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
def metric(a,m):
 x=np.array([z[m]-z['actual'] for z in a]);return {'n':len(x),'MAE':float(abs(x).mean()),'RMSE':float(np.sqrt((x*x).mean())),'bias':float(x.mean())}
methods=['frozen_hybrid','expected_fitted','direct_mean','five_retrained','direct_retrained']
rows=[]
for window in ['all_exposed','pre2026_exposed','2026_exposed']:
 for fam in ['H','P']:
  a=[z for z in xs if (z['role']=='H')==(fam=='H') and (window=='all_exposed' or (z['target_season']==2026)==(window=='2026_exposed'))]
  for m in methods:rows.append({'window':window,'family':fam,'model':m,**metric(a,m)})
write('Window_Validation.csv',rows)
lineage=[]
for p in sorted(D.glob('*.joblib')):
 m=joblib.load(p);old=D.parent/('direct-workload-correction' if p.name.startswith('direct') else 'full-workload-scenario')/p.name;before=joblib.load(old);fam=m.get('family',m['manifest'].get('family'));row={'artifact':p.name,'family':fam,'asof':m.get('asof',m['manifest'].get('asof')),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'numerical_refit':fam=='H','reused_unaffected':fam=='P','rows':m['manifest']['rows'],'original_rows':before['manifest']['rows']}
 if p.name.startswith('model'):
  row.update(original_residual_rows=before['manifest']['unknown_role_rows'],corrected_residual_rows=m['manifest']['unknown_role_rows'],original_calibrator_present=before['calibrator'] is not None,corrected_calibrator_present=m['calibrator'] is not None)
 lineage.append(row)
write('Artifact_Lineage.csv',lineage)
write('Remaining_AsOf_Role_Unidentifiable.csv',[{'id':a['mlbam_id'],'name':a['name'],'anchor':a['anchor'],'actual':a['actual'],'role_evidence':'no positive demonstrated MLB usage in previous three seasons after source repair','outcome':a['repaired_actual_state'],'future_role_claim':False} for a in xs if a['role']=='H' and a['repaired_forecast_role']=='uncertain'])
summary={'evaluation_cases':len(xs),'H_cases':sum(z['role']=='H' for z in xs),'P_cases':sum(z['role']!='H' for z in xs),'H_old_unknown_labels':sum(z['role']=='H' and z['actual_state']=='unknown_role' for z in xs),'H_repaired_unidentifiable_labels':sum(z['role']=='H' and z['repaired_actual_state']=='retention_unidentifiable' for z in xs),'H_asof_unidentifiable_before':sum(z['role']=='H' and z['forecast_role']=='uncertain' for z in xs),'H_asof_unidentifiable_after':sum(z['role']=='H' and z['repaired_forecast_role']=='uncertain' for z in xs),'H_input_repaired_cases':sum(z['role']=='H' and z['input_GP_repaired'] for z in xs),'H_target_repaired_cases':sum(z['role']=='H' and z['target_GP_repaired'] for z in xs),'H_total_labels_changed':sum(z['role']=='H' and z['actual_state'].replace('unknown_role','retention_unidentifiable')!=z['repaired_actual_state'] for z in xs),'H_fitted_artifacts':sum(a['family']=='H' for a in lineage),'P_reused_artifacts':sum(a['family']=='P' for a in lineage),'numerical_release':False,'recommendation':'retain preserved strong benchmark; repaired five-state hitter model warrants narrow independent confirmation, not production replacement'}
(D/'Results_Summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

"""Coverage-semantic correction only. Never changes model predictions or training."""
import json,gzip,csv
from pathlib import Path
from collections import Counter
D=Path(__file__).resolve().parent
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
events=[]
for p in (D/'verified').glob('transactions*.json.gz'):
 for t in json.loads(gzip.decompress(p.read_bytes())).get('transactions',[]):
  txt=t.get('description','').lower();kind='IL status event' if ('injured list' in txt or 'disabled list' in txt) else 'option/demotion' if 'optioned' in txt else 'recall/promotion' if 'recalled' in txt or 'selected the contract' in txt else 'other'
  events.append({'id':t.get('person',{}).get('id'),'date':t.get('date'),'effective_date':t.get('effectiveDate'),'type':t.get('typeCode'),'kind':kind,'description':t.get('description'),'source_file':p.name,'published_timestamp':None,'complete_absence_interval':False})
write('Dated_Transaction_Events.csv',events)
rows=list(csv.DictReader((D/'Coverage_Label_Correction.csv').open()))
for a in rows:
 if a['status']!='target_GP_verified':continue
 a['future_role_observation_status']='observed_from_complete_PA_matched_GP_census'
 if a['corrected_state']=='unknown_role':
  a['corrected_state']='retention_unidentifiable_asof'
  a['correction_note']='Future role is observed. Retention cannot be labeled because forecast-date role is unobserved; not a genuine future unknown-role outcome.'
 else:a['correction_note']='Retained/changed usage proxy becomes identifiable after targetGP verification.'
 a['numeric_model_retrained']=False
write('Coverage_Label_Correction.csv',rows)
summary={'events':len(events),'event_types':dict(Counter(a['kind'] for a in events)),'verified_target_GP_corrections':sum(a['status']=='target_GP_verified' for a in rows),'known_retention_proxy_labels':sum(a.get('corrected_state') in ['changed','retained_reduced','retained_high_usage'] for a in rows),'retention_unidentifiable_asof':sum(a.get('corrected_state')=='retention_unidentifiable_asof' for a in rows),'medical_absence_intervals_created':0,'forecasts_changed':False,'clinical_calibration_sample':False,'independent_holdout_created':False}
(D/'Evidence_Audit_Summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)

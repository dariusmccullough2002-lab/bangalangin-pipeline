"""Fixed-model coverage stress, not another selection candidate or new fit.
Reuses the two frozen census samples as forecast-date GP evidence when their
season is the anchor. Future target GP is never used as a forecast input.
"""
import importlib.util,sys,json,gzip,csv
from pathlib import Path
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('direct_research',D/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
GP={}
for year in [2018,2024]:
 p=D/'verified'/f'GP{year}.json.gz'
 if p.exists():
  for a in json.loads(gzip.decompress(p.read_bytes()))['stats'][0]['splits']:GP[a['player']['id'],year]=(float(a['stat']['plateAppearances']),float(a['stat']['gamesPlayed']))
original=r.e.observation
def observed(z,year):
 o=original(z,year);new=GP.get((z['id'],year))
 if z['role']=='H' and year==z['year'] and new and o['exposure'] is not None and abs(new[0]-o['exposure'])<1e-8 and o['GP'] is None:
  return o|{'GP':new[1],'GP_source':'official complete anchor-season census; PA-matched'}
 return o
rows=[]
for a in r.e.read(D/'Cases.json.gz'):
 if a['role']!='H' or a['anchor'] not in [2018,2024]:continue
 z=r.e.historical_z(a['mlbam_id'],a['anchor'],'H');o=original(z,z['year']);model=r.model(a['anchor'],'H');before=r.forecast(model,z)
 r.e.observation=observed
 try:after=r.forecast(model,z);role=r.scenario.forecast_role(z)[0];new=observed(z,z['year'])
 finally:r.e.observation=original
 rows.append({'id':a['mlbam_id'],'name':a['name'],'anchor':a['anchor'],'target_season':a['target_season'],'old_GP':o['GP'],'verified_GP':new['GP'],'missing_GP_resolved':o['GP'] is None and new['GP'] is not None,'before_role':a['forecast_role'],'after_role':role,'before_direct':before,'after_direct':after,'change':after-before,'actual':a['actual'],'future_inputs_used':False,'new_candidate':False})
r.csvout('Forecast_Date_Coverage_Sensitivity.csv',rows)
changed=[a for a in rows if a['missing_GP_resolved']]
r.put('Coverage_Sensitivity_Summary.json',{'eligible_cases':len(rows),'anchor_GP_gaps_resolved':len(changed),'forecasts_changed':sum(abs(a['change'])>1e-8 for a in changed),'mean_signed_prediction_change':sum(a['change'] for a in changed)/len(changed) if changed else None,'before':r.e.metric([(a['before_direct'],a['actual']) for a in changed]),'after':r.e.metric([(a['after_direct'],a['actual']) for a in changed]),'status':'exposed source-coverage sensitivity, not fit or selection; not adopted','new_medical_labels':0})
print('coverage sensitivity',len(changed),'PA-matched forecast-date gaps')

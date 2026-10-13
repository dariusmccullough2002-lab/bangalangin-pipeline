from pathlib import Path
import json,csv,collections,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import model as m
OUT=Path(__file__).parent
# Descriptive unique-player cohort: five observed calendar seasons after debut.
unique={}
for a in sorted(m.CO,key=lambda a:a['year']):
 if m.eligible(a) and a['mlbamId'] not in unique:unique[a['mlbamId']]=a
study={}
for f in ['H','P']:
 rows=[]
 for a in unique.values():
  if m.fam(a)!=f:continue
  debut=m.first(a)
  if debut is None or debut+4>2019:continue # Complete ordinary-year follow-up, no COVID volume.
  lag=next((t for t in range(5) if m.regular(a,debut+t)),None);rows.append({'id':a['mlbamId'],'name':a['name'],'debut':debut,'first_year_exposure':m.exposure(a['mlbamId'],debut,f),'regular_lag':lag})
 study[f]={'players':len(rows),'regular_same_year':sum(r['regular_lag']==0 for r in rows),'regular_next_calendar_year':sum(r['regular_lag']==1 for r in rows),'regular_years_2_to_4':sum(r['regular_lag'] in [2,3,4] for r in rows),'not_regular_within_five_years':sum(r['regular_lag'] is None for r in rows),'debut_volume_mean':float(np.mean([r['first_year_exposure'] for r in rows])),'debut_volume_median':float(np.median([r['first_year_exposure'] for r in rows]))}
# In a source ETA year, arrival is uncertain, so even a conditional half-season is not guaranteed.
eta=[]
for a in m.CO:
 if not m.eligible(a) or not a.get('ETA'):continue
 y=int(a['ETA'])
 if y>m.END or y==2020:continue
 debut=m.first(a);eta.append({'id':a['mlbamId'],'origin':a['year'],'name':a['name'],'family':m.fam(a),'source_eta':y,'first_mlb_year':debut,'arrived_by_eta':int(debut is not None and debut<=y),'exposure_in_eta_year':m.exposure(a['mlbamId'],y,m.fam(a))})
m.write_csv(OUT/'Published_ETA_Outcomes.csv',eta)
eta_summary={}
for f in ['H','P']:
 r=[a for a in eta if a['family']==f];eta_summary[f]={'snapshot_cases':len(r),'players':len({a['id'] for a in r}),'arrived_by_published_eta_fraction':float(np.mean([a['arrived_by_eta'] for a in r])),'mean_volume_in_eta_year':float(np.mean([a['exposure_in_eta_year'] for a in r])),'median_volume_in_eta_year':float(np.median([a['exposure_in_eta_year'] for a in r]))}
# Player-block bootstrap of differences, to avoid treating horizons/duplicate snapshots as independent.
rng=np.random.default_rng(20261013);uncertainty={}
for variant,path in [('ranked','Chronological_Cases.csv'),('rank_free','Rank_Free_Chronological_Cases.csv')]:
 data=list(csv.DictReader((OUT/path).open()))
 for f in ['H','P']:
  rows=[a for a in data if a['family']==f];groups=collections.defaultdict(list)
  for a in rows:
   groups[a['id']].append((float(a['arrival_pred'])-float(a['arrival_actual']))**2-(float(a['arrival_baseline'])-float(a['arrival_actual']))**2)
  units=np.array([np.mean(g) for g in groups.values()]);bootstrap=np.array([np.mean(rng.choice(units,len(units),replace=True)) for _ in range(2000)]);uncertainty[variant+'_'+f+'_arrival_Brier_difference']={'players':len(units),'player_mean_difference':float(np.mean(units)),'bootstrap_95_percent_interval':np.quantile(bootstrap,[.025,.975]).tolist()}
# Calibration bins are descriptive; no test-label refit.
calibration=[]
for variant,path in [('ranked','Chronological_Cases.csv'),('rank_free','Rank_Free_Chronological_Cases.csv')]:
 rows=list(csv.DictReader((OUT/path).open()))
 for f in ['H','P']:
  for target in ['arrival','regular']:
   for b in range(5):
    r=[a for a in rows if a['family']==f and min(4,int(float(a[target+'_pred'])*5))==b and (target=='arrival' or a['year']!='2020')]
    if r:calibration.append({'variant':variant,'family':f,'target':target,'bin':b,'rows':len(r),'players':len({a['id'] for a in r}),'mean_prediction':float(np.mean([float(a[target+'_pred']) for a in r])),'observed_fraction':float(np.mean([float(a[target+'_actual']) for a in r]))})
m.write_csv(OUT/'Calibration_Bins.csv',calibration)
(OUT/'Research_Findings.json').write_text(json.dumps({'complete_five_year_role_study':study,'published_ETA_study':eta_summary,'bootstrap':uncertainty,'covid_rule':'Five-year descriptive cohorts end by 2019. ETA volume years 2020 excluded. Arrival dates otherwise retain 2020.'},indent=2)+'\n');print(json.dumps({'role_study':study,'ETA_study':eta_summary,'bootstrap':uncertainty},indent=2))

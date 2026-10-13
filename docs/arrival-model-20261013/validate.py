"""Model contracts and chronological leakage checks, not implementation mirrors."""
from pathlib import Path
import json,csv,gzip,hashlib,re,sys
import numpy as np
P=Path(__file__).parent;ROOT=P.parents[1];D=json.loads((ROOT/'data/arrival-workload-model.json').read_text());C=json.loads((P/'Selection.json').read_text());assert C['selection_outcome_end']==2018 and C['rank_free']['selection_outcome_end']==2018
H=json.load(gzip.open(P/'inputs/Historical_Seasons.json.gz','rt'));assert {(r['year'],r['family']) for r in H['coverage']}=={(y,f) for y in range(2010,2026) for f in ['H','P']};assert all(r['complete_source'] for r in H['coverage']);assert len({(s['mlbamId'],s['year'],s['family']) for s in H['seasons']})==len(H['seasons'])
for a in D['players'].values():
 annual=a['annual'];assert len(annual)==8;mass=sum(r['first_mlb_probability'] for r in annual);assert abs(mass+a['no_mlb_by_horizon_probability']-1)<1e-9
 prev_arr=prev_reg=0
 for i,r in enumerate(annual):
  assert r['year']==2027+i;assert 0<=r['mlb_active_probability']<=r['mlb_arrived_by_year']+1e-9<=1+1e-9;assert prev_arr<=r['mlb_arrived_by_year'];assert prev_reg<=r['regular_role_reached_by_year']<=r['mlb_arrived_by_year']+1e-9;assert np.isfinite(r['expected_workload']) and r['expected_workload']>=0;prev_arr=r['mlb_arrived_by_year'];prev_reg=r['regular_role_reached_by_year']
 assert abs(sum(a['first_regular_mass'])+a['regular_not_reached_by_horizon_probability']-1)<1e-9
 assert a['inputs']['year']==2027
morales=D['players']['06ibo'];assert abs(morales['inputs']['age']-20.52)<.02;assert morales['published_eta']['value']=='2030';assert morales['annual'][0]['expected_workload']<morales['conditional_debut_year_workload'];assert morales['annual'][0]['regular_role_reached_by_year']<.1
# Right censoring and verified zero are distinct in the estimator.
sys.path.insert(0,str(P));import model
pool=model.donors(2013);assert all(d['debut']+d['duration']-1<=2013 for d in pool);assert any(0 in d['workload'] for d in pool);assert any(d['duration']<8 for d in pool);assert all(d['debut']!=2020 for d in model.donors(2025))
for name in ['Chronological_Cases.csv','Rank_Free_Chronological_Cases.csv']:
 rows=list(csv.DictReader((P/name).open()));assert {int(r['origin']) for r in rows}=={2019,2020};assert all(int(r['year'])>=int(r['origin']) and int(r['year'])<=2025 for r in rows)
html=(ROOT/'trade-analyzer-beta/index.html').read_text();packed=re.search(r"const packed='([^']+)'",html)[1];frozen=json.loads((ROOT/'docs/prospect-timing-20261013/Summary.json').read_text());assert hashlib.sha256(packed.encode()).hexdigest()==frozen['packed_catalog_sha256']
report={'status':'PASS','current_forecasts':len(D['players']),'forecast_years':8,'probability_conservation':True,'regular_probability_bounded_by_arrival':True,'active_probability_bounded_by_arrival':True,'source_year_coverage_complete':True,'right_censoring_checked':True,'chronological_origins':[2019,2020],'selection_label_end':2018,'neutral_catalog_preserved':True,'new_competitive_fit_values':0}
(P/'Contract_Validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

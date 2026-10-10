"""Pre-scoring population and field-coverage inventory; no model fit."""
import importlib.util,json,csv,gzip
from pathlib import Path
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('preserved_direct',D.parent/'direct-workload-correction/run.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
e=p.e;s=p.scenario
BASE=e.read(D.parent/'direct-workload-correction/Cases.json.gz')
def dump(name,a):
 b=json.dumps(a,allow_nan=False).encode();(D/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def write(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def build():
 rows=e.training(2026,calendar=True,family='H');rows=[a for a in rows if a['year']!=2020]
 records={};requests={};out=[]
 for use,pool in [('training',[(a['z'],a['year']) for a in rows]),('evaluation',[(e.historical_z(a['mlbam_id'],a['anchor'],a['role']),a['target_season']) for a in BASE if a['role']=='H'])]:
  for z,ty in pool:
   refs=[('target',ty)]+[('forecast_input',year) for year in range(z['year'],z['year']-4,-1)]
   for kind,year in refs:
    o=e.observation(z|{'year':max(z['year'],year)},year)
    rec=(z['id'],year);requests.setdefault(rec,set()).add(use+':'+kind)
    records.setdefault(rec,o)
   lab=s.target_label(z);obs=[e.observation(z,y) for y in range(z['year'],z['year']-4,-1)]
   out.append({'use':use,'id':z['id'],'anchor':z['year'],'target_year':ty,'target_GP_missing':lab['observation']['exposure']>0 and lab['observation']['GP'] is None,'input_GP_missing':any(o['exposure'] is not None and o['exposure']>0 and o['GP'] is None for o in obs),'asof_role_unidentifiable':s.forecast_role(z)[0]=='uncertain','old_state':s.STATES[lab['state']]})
 logs=[{'id':ident,'year':year,**o,'uses':'|'.join(sorted(requests[ident,year]))} for (ident,year),o in records.items()]
 write('Pre_Repair_Records.csv',logs);write('Pre_Repair_Cases.csv',out)
 seasons=sorted({a['year'] for a in logs if a['exposure'] is not None and a['exposure']>0 and a['GP'] is None})
 summary={'training_case_rows':len(rows),'evaluation_H_cases':1487,'unique_player_seasons':len(logs),'required_census_seasons':seasons,'unique_positive_missing_GP':sum(a['exposure'] is not None and a['exposure']>0 and a['GP'] is None for a in logs),'by_use':{u:{'n':sum(a['use']==u for a in out),'missing_target_GP':sum(a['use']==u and a['target_GP_missing'] for a in out),'missing_input_GP':sum(a['use']==u and a['input_GP_missing'] for a in out),'unidentifiable_asof':sum(a['use']==u and a['asof_role_unidentifiable'] for a in out)} for u in ['training','evaluation']}}
 dump('Pre_Repair_Inventory.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':build()

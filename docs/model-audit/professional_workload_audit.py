"""Experimental workload channel. No catalog or production writes.
Run: python professional_workload_audit.py RECOVERY_ROOT CATALOG OUTPUT_DIR
Age<=26 is an inventory screen, not a new fitted development threshold.
Only verified, nonoverlapping affiliated MiLB season totals may be added.
Unknown totals remain unknown; zero is never imputed for missing evidence.
"""
import sys,json,csv,copy,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
root,cat,out=map(Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root.resolve()/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
v,r,old=m.v,m.r,m.old
assets=json.loads(cat.read_text())['assets']
# Independent workload evidence only. Decimal IP, not baseball .1/.2 notation.
evidence={('061yu',2025):{'minor_ip':63+1/3,'source':'https://baseballsavant.mlb.com/savant-player/jacob-misiorowski-694819','scope':'2025 AAA aggregate; MLB excluded; not sum of aggregate plus splits'}}
def combined_workload(p,rr):
 rows=[z for z in v.seasons(p,rr) if 2023<=z['year']<=2026 and z['role']==rr and r.exposure(z['stat'],rr)>0]
 if not rows:return None
 weights={2023:.1,2024:.2,2025:.3,2026:.4};mass=sum(weights[z['year']] for z in rows)
 ips=[z['stat']['IP']+evidence.get((p['id'],z['year']),{}).get('minor_ip',0) for z in rows]
 recent=sum(x*weights[z['year']]/mass for z,x in zip(rows,ips));healthy=float(np.median(sorted(ips,reverse=True)[:2]));pw=1/(len(rows)+3)
 return min(v.cf.cap(rr),(1-pw)*(.7*recent+.3*healthy)+pw*r.REFERENCE[rr])
owned=[a for a in assets if a.get('id') in old.players and a.get('owner') and a['owner'].lower() not in ['free agent','free agents','fa','unowned']]
season_rows=[];league=[];changes=[]
for a in owned:
 p=old.players[a['id']];au=a['audit'].get('MLB',a['audit']);rr=au.get('role');projection=au.get('projection',{});age=p.get('age');hist=v.seasons(p,rr) if rr in ['H','SP','RP'] else []
 league.append({'id':a['id'],'name':a['name'],'owner':a['owner'],'age':age,'role':rr,'baseline_workload':projection.get('PA',projection.get('IP')),'status':'MLB projection' if projection else 'Prospect/no MLB projection; no invented workload'})
 if rr not in ['SP','RP']:continue
 for z in hist:
  season_age=age-(2026-z['year']) if age is not None else None
  if not (2023<=z['year']<=2026 and season_age is not None and season_age<=26):continue
  e=evidence.get((a['id'],z['year']))
  season_rows.append({'id':a['id'],'name':a['name'],'owner':a['owner'],'season':z['year'],'season_age':season_age,'role':z['role'],'MLB_IP':z['stat'].get('IP'),'verified_MiLB_IP':e['minor_ip'] if e else None,'combined_IP':z['stat']['IP']+e['minor_ip'] if e else None,'status':'Verified combined workload' if e else 'MiLB coverage unverified; baseline retained','source':e['source'] if e else ''})
 if not any((a['id'],z['year']) in evidence for z in hist):continue
 original=v.recent_forecast;work=combined_workload(p,rr)
 def experimental(q,role,scenario='base'):
  f=original(q,role,scenario)
  if q['id']==p['id'] and role==rr and f:
   audit=copy.deepcopy(f[2]);audit['projected_workload']=work
   return f[0],work,audit
  return f
 v.recent_forecast=experimental
 try:
  paths,audit=m.paths(p);new=audit.get('MLB',audit)
  assert new['projection_audit']['talent_rates']==au['projection_audit']['talent_rates']
  changes.append({'id':a['id'],'name':a['name'],'baseline':projection,'experimental':new['projection'],'baseline_neutral':a['values']['neutral']['display'],'experimental_neutral':m.competitive(paths,'neutral')['display'],'MLB_talent_rates_unchanged':True})
 finally:v.recent_forecast=original
for name,rows in [('League_Workload_Coverage.csv',league),('Young_Pitcher_Season_Coverage.csv',season_rows)]:
 with (out/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result={'status':'EXPERIMENTAL ONLY; production untouched','owned_player_count':len(owned),'young_pitcher_seasons_screened':len(season_rows),'young_pitchers_with_MLB_history':len(set(z['id'] for z in season_rows)),'verified_combined_seasons':sum(z['verified_MiLB_IP'] is not None for z in season_rows),'unverified_seasons':sum(z['verified_MiLB_IP'] is None for z in season_rows),'changes':changes,'baseline_sha256':hashlib.sha256(cat.read_bytes()).hexdigest(),'limitations':['Frozen research lacks comprehensive MiLB season totals. League-wide numerical application is blocked for missing evidence.','Includes MLB-exposed pitchers age<=26 during2023–26; prospects without MLB histories retained in league coverage, not converted to MLB forecasts.','Same-season MiLB workload alone; MLB K/ER/SV/HLD/QA3 rates unchanged. Existing caps and age curves unchanged.','No injury workload restoration, start-role conversion, or extrapolation of incomplete seasons.','MiLB-only earlier seasons are not inserted without verified inputs and a separately validated season-weighting policy.']}
(out/'Professional_Workload_Experiment.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['changes','limitations']}))

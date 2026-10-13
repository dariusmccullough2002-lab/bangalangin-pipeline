"""Read preserved catalog/history; build display-only access and workload diagnostics."""
from pathlib import Path
import json,re,gzip,base64,math,collections,csv,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
h=(ROOT/'trade-analyzer-beta/index.html').read_text();cat=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",h)[1])))
refs=read(ROOT/'docs/value-audit-20261012/inputs/model-evidence.json');starter=read(ROOT/'data/starter-display-scenarios.json');role=read(ROOT/'data/role-display-scenarios.json')
def finite(s,key):return isinstance(s.get(key),(int,float)) and math.isfinite(s[key])
def score(s,kind):
 q=refs['category_references'];disp=refs['category_dispersion'];exposure='PA' if kind=='H' else 'IP';reference=refs['reference_workload'][kind]
 if not finite(s,exposure) or s[exposure]<=0:return None
 t={k:float(v)*reference/s[exposure] for k,v in s.items() if isinstance(v,(int,float))}
 try:
  if kind=='H':
   ab=t['AB'];den=ab+t['BB']+t['HBP']+t['SF'];ops=(t['H']+t['BB']+t['HBP'])/den+t['TB']/ab
   v=[t[k] for k in ['HR','R','RBI','SB']]+[t['H']-q['AVG']*ab,(ops-q['OPS'])*ab];d=disp['H']
  else:v=[-t['ER'],t['K'],3*t['SV']+2*t['HLD'],t['QA3'],t['K']-q['KBB']*t['BB'],q['WHIP']*t['IP']-t['H']-t['BB']];d=disp['P']
  return sum(z/w for z,w in zip(v,d))
 except (KeyError,ZeroDivisionError):return None
def positions(a):
 out=set()
 for p in re.split('[, /]+',a.get('position','')):
  if p in ['CF','LF','RF']:p='OF'
  if p=='CI':out.update(['1B','3B'])
  elif p=='MI':out.update(['2B','SS'])
  else:out.add(p)
 return out
def latest(a):return next((s for s in reversed(a.get('career_profile',{}).get('seasons',[])) if s['year']==2026),None)
# A minimum observed sample establishes an evidenced pool, not a zero-value rule.
pool=[]
for a in cat['assets']:
 kind=a['audit']['role'];s=latest(a);projection=a['audit'].get('projection',{})
 if a.get('owner')!='Free agent' or a['audit']['kind']!='MLB' or kind not in ['H','SP','RP'] or not s:continue
 if not a.get('availability_status',{}).get('mlbam_verified'):continue
 key='AB' if kind=='H' else 'IP';minimum=150 if kind=='H' else 30
 if s['role']!=kind or not finite(s['stat'],key) or s['stat'][key]<minimum:continue
 quality=score(projection,kind)
 if quality is None:continue
 pool.append(dict(id=a['id'],name=a['name'],kind=kind,position=a.get('position',''),positions=sorted(positions(a)),quality=quality,expected_exposure=projection['PA' if kind=='H' else 'IP'],exposure_unit='PA' if kind=='H' else 'IP',ownerAsOf=a.get('ownerAsOf',cat['asOf']),identity=a['playerIdentity'],observed_exposure=s['stat'][key]))
byrole={k:sorted([a for a in pool if a['kind']==k],key=lambda a:(-a['quality'],a['id'])) for k in ['H','SP','RP']}
players={};decompositions=[]
for a in cat['assets']:
 kind=a['audit']['role']
 if kind not in ['H','SP','RP','H+SP']:continue
 p=a['audit'].get('projection',{});unit='PA' if kind=='H' else 'IP';hist=a.get('career_profile',{}).get('seasons',[])
 choices=[]
 if a['audit']['kind']=='MLB' and kind in byrole:
  for c in byrole[kind]:
   if c['id']==a['id'] or c['identity']==a['playerIdentity']:continue
   if kind=='H' and not ((positions(a)&set(c['positions']))-{'UT','DH',''}):
    if not (positions(a)<={'UT','DH',''}):continue
   choices.append(c)
   if len(choices)==3:break
 info=dict(name=a['name'],role=kind,alternatives=choices,pool_count=len(byrole.get(kind,[])),replacement_status='Dated modeled alternatives; current availability, legal roster room and claim competition unverified',replacement_method='Same pitching role or shared hitter eligibility; ordered by inherited six-category talent score at role-specific reference exposure. These are comparison candidates, not guaranteed equivalent replacements or acquisition prices.',unit=unit)
 if kind in ['SP','RP'] and a['audit']['kind']=='MLB':
  pa=a['audit'].get('projection_audit',{});capacity=pa.get('projected_workload');expected=p.get('IP');full=(starter['players'].get(a['id'],{}).get('line',{}).get('IP') if kind=='SP' else role['players'].get(a['id'],{}).get('workload'))
  history=[dict(year=s['year'],role=s['role'],IP=s['stat'].get('IP'),source=s.get('source','preserved history')) for s in hist if s['year']>=2023 and finite(s['stat'],'IP')]
  info['durability']=dict(expected_IP=expected,starting_workload_IP=capacity,full_role_IP=full,cohort_factor=(expected/capacity if expected and capacity and capacity>0 else None),history=history,observed_IP_range=[min(s['IP'] for s in history),max(s['IP'] for s in history)] if history else None,observed_roles=sorted({s['role'] for s in history}),age=a.get('career_profile',{}).get('age'),diagnosis='No verified diagnosis or individual recovery probability in this diagnostic',uncertainty='Observed workload range and conditional scenario gap; not a forecast interval or injury probability',double_discount_audit='Starting workload already blends recent usage. The future cohort factor is applied once; their overlapping availability effects remain uncalibrated. No additional durability haircut added.')
  decompositions.append(dict(id=a['id'],name=a['name'],role=kind,starting_IP=capacity,expected_IP=expected,full_role_IP=full,cohort_factor=info['durability']['cohort_factor'],observed_min=info['durability']['observed_IP_range'][0] if history else None,observed_max=info['durability']['observed_IP_range'][1] if history else None))
 if choices or 'durability' in info:players[a['id']]=info
# Reuse cached historical pitcher cases; do not train against current surviving players.
cases=json.loads(gzip.decompress((D/'inputs/Historical_Pitcher_Cases.json.gz').read_bytes()));seen=set();usable=[]
for r in cases:
 key=(r['mlbam_id'],r['anchor'],r['target_year'])
 if key in seen:continue
 seen.add(key)
 if r['target_year']>2025 or r['target_year']==2020 or r['role'] not in ['SP','RP']:continue
 if not finite(r.get('actual',{}),'IP') or not finite(r.get('baseline',{}),'IP'):continue
 usable.append(r)
validation=[]
for kind in ['SP','RP']:
 for group in ['all','young_under26','established26plus']:
  rows=[r for r in usable if r['role']==kind and (group=='all' or ((r['age']<26)==(group=='young_under26')))]
  if not rows:continue
  for model in ['baseline','debut_opportunity']:
   supported=[r for r in rows if finite(r.get(model,{}),'IP')];err=np.array([r[model]['IP']-r['actual']['IP'] for r in supported]);validation.append(dict(role=kind,group=group,model=model,n=len(supported),unique_players=len({r['mlbam_id'] for r in supported}),MAE=float(np.mean(abs(err))),bias=float(np.mean(err)),error_P10=float(np.quantile(err,.1)),error_P90=float(np.quantile(err,.9)),actual_zero_count=sum(r['actual']['IP']==0 for r in supported)))
metadata=dict(schemaVersion=1,asOf=cat['asOf'],pool_counts={k:len(v) for k,v in byrole.items()},sample_screen='Positive verified 2026 MLB sample: hitters at least150 AB; pitchers at least30 IP, matching observed and forecast role. Excluded/missing/small-sample records are unknown, not worthless.',access_limits='Snapshot evidence only. No live claims/drops feed, legal open slots or access probabilities are available. Rounds6–20 are acquisition evidence only and never valued assets.',durability_limits='Previously exposed chronological cases with recorded positive target seasons; old baseline and debut-opportunity benchmark, not a fresh test of the current forecast. This sample cannot estimate zero-IP or injury probabilities. No calibrated player-specific IP interval.',forecast_changes=0,trade_value_changes=0,players=players,historical_validation=validation)
# Normalize repeated candidate records and shared caveats for a smaller public payload.
metadata['candidates']={c['id']:c for c in pool}
metadata['commonDurability']=dict(diagnosis='No verified diagnosis or individual recovery probability in this diagnostic',uncertainty='Observed workload range and conditional scenario gap; not a forecast interval or injury probability',double_discount_audit='Recent usage and the cohort factor can overlap in availability conservatism; no additional penalty added.')
for entry in players.values():
 entry['alternatives']=[c['id'] for c in entry['alternatives']]
 for key in ['replacement_status','replacement_method']:entry.pop(key,None)
 if 'durability' in entry:
  for key in metadata['commonDurability']:entry['durability'].pop(key,None)
(ROOT/'data/access-durability.json').write_text(json.dumps(metadata,separators=(',',':'),ensure_ascii=False)+'\n')
for name,obj in [('Summary.json',{k:v for k,v in metadata.items() if k not in ['players','candidates']}),('Replacement_Pool.json',pool),('Workload_Decomposition.json',decompositions)]: (D/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
for name,rows in [('Chronological_Validation.csv',validation),('Workload_Decomposition.csv',decompositions)]:
 with (D/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(D/'Report.md').write_text('# Replacement access and pitcher workload diagnostics\n\nDD values and all forecasts are unchanged. The new sidecar displays source-dated comparison alternatives and separates expected IP, forecast starting capacity and conditional full-role IP.\n\n'+metadata['sample_screen']+'\n\n'+metadata['access_limits']+'\n\n'+metadata['durability_limits']+'\n\n## Pool counts\n\n'+str(metadata['pool_counts'])+'\n\n## Durability validation\n\n|Role|Group|Benchmark|Cases|MAE IP|Bias IP|\n|---|---|---|---:|---:|---:|\n'+''.join(f"|{r['role']}|{r['group']}|{r['model']}|{r['n']}|{r['MAE']:.2f}|{r['bias']:+.2f}|\n" for r in validation)+'\nThe saved historical release decision retained its strong benchmark. These previously inspected cases do not authorize switching the live workload forecast. Recent workload and the inherited cohort multiplier may overlap in availability conservatism; this audit exposes their separate numerical factors instead of claiming that a mechanical duplicate penalty was found.\n\nSaves and holds remain in the existing forecasts; no permanent closer role is assumed. Small-sample prospects do not receive invented full MLB workloads or false replacement scarcity. A fresh dated free-agent export, transaction history and verified lineup slots would permit more precise access estimates.\n')
print(json.dumps(dict(players=len(players),pool_counts=metadata['pool_counts'],validation=validation[:2]),indent=2))

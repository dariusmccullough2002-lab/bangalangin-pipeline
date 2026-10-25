"""Offline bench sensitivity using the supplied exact optimizer, saved current assets and explicit assumptions.
No fit to trades, no transaction-vintage backtest, no production imports/writes.
"""
import sys,json,gzip,random,collections,hashlib
from pathlib import Path
import numpy as np
R=Path('docs/valuation-priorities-20261024');sys.path.insert(0,str(R/'reference'))
import rostermodel as rm
D=json.loads(gzip.decompress((R/'Frozen_Inputs.json.gz').read_bytes()));A=D['assets'];by={a['id']:a for a in A};teams=[t['name'] for t in D['teams']]
# Explicit existing career stats replace pre-2023-missing and PA-to-AB proxy where supported.
def eligibility(a):
 cp=a.get('career_profile') or {};seasons=cp.get('seasons') or [];role=a['audit'].get('role')
 if role=='H+SP':return None
 key='IP' if role in ['SP','RP'] else 'AB';limit=162 if key=='IP' else 503
 if seasons:
  vals=[s.get('stat',{}).get(key) for s in seasons if s.get('role') in (['SP','RP'] if key=='IP' else ['H'])]
  if not vals or any(not isinstance(v,(int,float)) for v in vals):return None
  total=sum(vals)
  if total>limit:return False
  ids=cp.get('identifiers') or {};first=ids.get('first_mlb_year')
  if first is not None and first>=2010 and cp.get('coverage','').startswith('all cached MLB seasons'):return True
 if a['audit']['kind']=='prospect':return True # pre-debut classification; explicitly recorded as proxy, not a fresh eligibility capture
 return None
elig={a['id']:eligibility(a) for a in A if a['audit']['kind']!='pick'}
rm.minors_eligible=lambda a:elig.get(a['id']) is True
# All non-neutral timing removed: only neutral-discount first-three-year share, with supported ETA alignment.
def near(a):
 path=a.get('alignedAnnualUtility')
 if not path or len(path)!=8:return 0.0
 total=sum(x*.88**t for t,x in enumerate(path));return sum(x*.88**t for t,x in enumerate(path[:3]))/total if total>0 else 0.0
rm.near_term_share=near
rng=random.Random(20261024);owned={t:[a for a in A if a.get('owner')==t and a['audit']['kind']!='pick' and a['values']['neutral']['display']>0] for t in teams};cases=[]
for size in [1,2,3,4,6]:
 found=0;attempts=0;seen=set()
 while found<40 and attempts<50000:
  attempts+=1;t,u=rng.sample(teams,2)
  if len(owned[t])<size:continue
  out=rng.sample(owned[t],size);price=sum(a['values']['neutral']['display'] for a in out)
  options=[a for a in owned[u] if .9*price<=a['values']['neutral']['display']<=1.1*price]
  if not options:continue
  inc=rng.choice(options);all_=out+[inc]
  if len(set(a.get('playerIdentity',a['id']) for a in all_))!=len(all_):continue
  sig=tuple(sorted(a['id'] for a in out))+(inc['id'],)
  if sig in seen:continue
  seen.add(sig);found+=1;cases.append(dict(id=f'{size}-{found}',size=size,teams=[t,u],sides=[[a['id'] for a in out],[inc['id']]]))
rows=[]
for rho in [0,.25,.5,1]:
 # Equal no-waiver baseline in both counterfactuals. IR use follows supplied rule: MLB IL membership not required.
 L=rm.League(D,dict(rho=rho,fa_on=False,ir_any=True));L.slack={} # never invent eligibility slack
 for c in cases:
  rs=[]
  for side in range(2):
   r=L.delta(L.base_owner,c['teams'][side],c['sides'][side],c['sides'][1-side]);rs.append(r)
  rows.append(dict(**c,rho=rho,results=rs))
 print(f'rho={rho}: {len(cases)} two-sided cases complete',flush=True)
summary={}
for size in [1,2,3,4,6]:
 summary[size]={}
 for rho in [0,.25,.5,1]:
  vals=[r for r in rows if r['size']==size and r['rho']==rho];valid=[r for r in vals if all(x['pre_trade_roster_legal'] for x in r['results'])]
  summary[size][rho]=dict(total=len(vals),baselineFeasible=len(valid),baselineRepairsNeeded=len(vals)-len(valid),meanEffects=[float(np.mean([r['results'][s]['candidate']-r['results'][s]['baseline'] for r in valid])) if valid else None for s in range(2)])
checks=[]
for r in rows:
 if r['rho']==1:
  for side,x in enumerate(r['results']):
   if x['pre_trade_roster_legal'] and not x['new_drops'] and abs(x['candidate']-x['baseline'])>1e-5:checks.append(f"{r['id']}/{side}: capacity-only identity failed")
# Dates and missingness: current valuations cannot establish historical fair prices.
coverage=dict(eligibilityKnown=sum(x is not None for x in elig.values()),eligibilityUnknown=sum(x is None for x in elig.values()),careerTotalsSupported=sum(bool(a.get('career_profile',{}).get('seasons')) for a in A),transactionTrades=len(D['trades']),transactionDateRange=[min(t['date'] for t in D['trades']),max(t['date'] for t in D['trades'])])
result=dict(inputSha256=hashlib.sha256((R/'Frozen_Inputs.json.gz').read_bytes()).hexdigest(),seed=20261024,coverage=coverage,summary=summary,failedChecks=checks,cases=rows,assumptions=['Original supplied exact MILP optimizer, unchanged; minor-eligibility and ETA-aligned near-term-share inputs improved explicitly by wrapper.','No waiver additions for either side; no fabricated eligibility slack; IR pool eight under supplied rule.','Bench credit applies only to neutral-discounted first-three-year portion; future asset value retained. No contender/rebuild curve applied.','Infeasible starting rosters recorded separately and excluded from headline mean effects.','No daily schedules or weekly category simulation; static assignment does not impose all required-active minimums or model suspension restrictions. Not legal-trade certification.','Unknown minors eligibility gets no minors credit; pre-debut prospect classification remains a proxy.','Bench credits 0/.25/.5/1 are assumptions, not learned parameters. No optimal bench coefficient selected.','Current ownership snapshots and current values cannot validate historical trade fairness.'])
(R/'Bench_Results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'coverage':coverage,'summary':summary,'failedChecks':checks},indent=2))
if checks:sys.exit(1)

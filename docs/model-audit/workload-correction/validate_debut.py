"""Debut-only capacity sensitivity and past-only chronological workload evaluation.
No production changes. Candidate rules fixed before scoring; no named exceptions.
"""
import sys,json,copy,collections,math,functools,csv,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(sys.argv[1]).resolve();CAT=Path(sys.argv[2]).resolve();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
from debut_audit import load_index,inventory
v,r,old=m.v,m.r,m.old
catalog=json.loads(CAT.read_text());index,complete=load_index();appear=v.appearance_history()
hist={};lookup={};first={};profiles={}
for p in v.cf.PROFILES.values():
 ident=p.get('identifiers',{}).get('mlbamId')
 if not ident:continue
 rows=[z for z in p['seasons'] if z['role']!='H' and z['stat'].get('IP',0)>0]
 if rows:
  profiles[ident]=p;first[ident]=min(z['year'] for z in rows)
for a in old.AN:
 z=copy.deepcopy(a)
 if z['role']!='H':z['role']=v.observed_role(appear.get((z['id'],z['year']),{}),z['role'])
 hist.setdefault((z['id'],'H' if z['role']=='H' else 'P'),[]).append(z);lookup[z['id'],z['year'],'H' if z['role']=='H' else 'P']=z
for (ident,stream),rows in hist.items():
 if stream=='P' and ident not in first:
  earliest=min(z['year'] for z in rows)
  if earliest>2010:first[ident]=earliest
def milb(ident,year):
 if complete.get(year,set())!=set(range(11,17)):return None
 return sum(z['outs'] for z in index.get((ident,year),[]))/3
def forecast(rows,rr,year,ident,method='baseline',strict=False,pandemic='raw'):
 rows=[z for z in rows if year-3<=z['year']<=year and z['role']==rr and r.exposure(z['stat'],rr)>0]
 if not rows or not any(z['year']>=year-2 for z in rows):return None
 weights={year-3:.1,year-2:.2,year-1:.3,year:.4};mass=sum(weights[z['year']] for z in rows)
 mlb=[r.exposure(z['stat'],rr) for z in rows];workloads=mlb.copy();debut=first.get(ident)
 # Capacity ledger is universal. Opportunity attenuation uses only observed MLB evidence as of date.
 for i,z in enumerate(rows):
  if method=='baseline' or rr=='H' or z['year']!=debut:continue
  minor=milb(ident,debut)
  if minor is None:continue
  professional=mlb[i]+minor
  opportunity=1.
  if method=='debut_opportunity':
   later=max([r.exposure(t['stat'],rr) for t in rows if t['year']>debut]+[mlb[i]])
   opportunity=min(1,later/professional) if professional else 0
  workloads[i]+=minor*opportunity
 if pandemic=='omit':
  keep=[i for i,z in enumerate(rows) if z['year']!=2020]
  if keep:rows=[rows[i] for i in keep];mlb=[mlb[i] for i in keep];workloads=[workloads[i] for i in keep];mass=sum(weights[z['year']] for z in rows)
 elif pandemic=='bounded_capacity':
  for i,z in enumerate(rows):
   if z['year']==2020:
    earlier=[r.exposure(t['stat'],rr) for t in hist.get((ident,'H' if rr=='H' else 'P'),[]) if t['year']<2020 and t['role']==rr]
    if earlier:workloads[i]=min(mlb[i]*162/60,max(earlier))
 recent=sum(ip*weights[z['year']]/mass for z,ip in zip(rows,workloads));healthy=float(np.median(sorted(workloads,reverse=True)[:2]));pw=1/(len(rows)+3)
 prior=float(np.median([r.exposure(z['stat'],rr) for z in old.cal if z['role']==rr]));cap=asof_cap(rr,year) if strict else v.cf.cap(rr)
 work=min(cap,(1-pw)*(.7*recent+.3*healthy)+pw*prior)
 # Always actual MLB counts / actual MLB innings, including shortened-season rates.
 mlbrecent=sum(ip*weights[z['year']]/mass for z,ip in zip(rows,mlb));strength=100 if rr=='H' else 30
 rates={k:(sum(z['stat'].get(k,0)*weights[z['year']]/mass for z in rows)+strength*old.prior[rr][k])/(mlbrecent+strength) for k in old.fields[rr]}
 return rates,work
@functools.lru_cache(None)
def asof_cap(rr,year):
 xs=[r.exposure(z['stat'],rr) for z in old.AN if z['year']<=year and z['role']==rr and r.exposure(z['stat'],rr)>0 and z['year']!=2020]
 return float(np.quantile(xs,.98))
@functools.lru_cache(None)
def asof_curve(rr,age,year):
 # Only completed one-year pairs, identity holdout excluded. No 8-year future labels or full-history cap.
 stream='H' if rr=='H' else 'P';pool=[]
 for (ident,s),rows in hist.items():
  if s!=stream or ident%5==0:continue
  for z in rows:
   if not 2011<=z['year']<year or z['role']!=rr or z['year'] in [2019,2020]:continue
   e=r.exposure(z['stat'],rr);a=r.age_at(ident,z['year'])
   if a is None or not math.isfinite(a) or e<(250 if rr=='H' else 80 if rr=='SP' else 30):continue
   target=lookup.get((ident,z['year']+1,stream));pool.append((ident,a,z['stat'],target['stat'] if target else {}))
 sample=[z for z in pool if abs(z[1]-age)<=2]
 if len({z[0] for z in sample})<20:sample=[z for z in pool if abs(z[1]-age)<=4]
 if not sample:sample=pool
 before=sum(r.exposure(z[2],rr) for z in sample);after=sum(r.exposure(z[3],rr) for z in sample);n=len({z[0] for z in sample});shrink=n/(n+40)
 rates={}
 for k in old.fields[rr]:
  a=sum(z[2].get(k,0) for z in sample)/before if before else 0;b=sum(z[3].get(k,0) for z in sample)/after if after else 0
  rates[k]=1 if k in ['IP','PA','AB'] or not a else max(0,1+shrink*(b/a-1))
 for k in ['SV','HLD']:
  if k in rates:rates[k]=min(1,rates[k])
 return {'workload':after/before if before else 1,'rates':rates,'training_pairs':len(sample),'latest_training_target':year}
def project(f,rr,age,year,strict=False):
 rates,work=f
 if strict:c=asof_curve(rr,int(round(age)),year)
 else:
  q=int(np.searchsorted(v.base.CUTS[rr],r.surplus({k:x*work for k,x in rates.items()},rr)/work*r.REFERENCE[rr]));c=v.curve(rr,int(round(age)),q)['path'][0]
 s={k:x*c['rates'].get(k,1)*work*c['workload'] for k,x in rates.items()}
 if rr=='H':return v.reconcile(s)
 s['QA3']=min(s['QA3'],s['IP']/5);return s
def score(cases,methods,fields):
 result={}
 for group in sorted({g for z in cases for g in z['groups']}):
  rows=[z for z in cases if group in z['groups']];metrics={}
  for k in fields:
   valid=[z for z in rows if k in z['actual'] or not z['actual']]
   metrics[k]={method:{'n':len(valid),'MAE':float(np.mean([abs(z[method].get(k,0)-z['actual'].get(k,0)) for z in valid])),'bias':float(np.mean([z[method].get(k,0)-z['actual'].get(k,0) for z in valid]))} for method in methods} if valid else {}
  result[group]={'n':len(rows),'metrics':metrics}
 return result
def pitching_projection(audit,rr):
 audit=audit.get('MLB',audit)
 component=audit.get('two_way_components',{}).get(rr,audit)
 return component.get('audit',component)['projection']
methods=['baseline','debut_raw','debut_opportunity'];cases=[]
anchors=[2016,2017,2018,2021,2022,2023,2024]
for (ident,stream),history in hist.items():
 if stream!='P' or ident%5:continue
 for year in anchors:
  z=lookup.get((ident,year,'P'))
  if not z or z['stat'].get('IP',0)<=0:continue
  age=r.age_at(ident,year)
  if age is None or not math.isfinite(age):continue
  rr=z['role'];f={method:forecast(history,rr,year,ident,method,True) for method in methods}
  if any(q is None for q in f.values()):continue
  assert all(f[method][0]==f['baseline'][0] for method in methods)
  target=lookup.get((ident,year+1,'P'));info=appear.get((ident,year),{});gp=info.get('GP',0);gs=info.get('GS',0)
  groups=['all',rr,'young' if age<=26 else 'established',f'anchor_{year}']
  debut=first.get(ident)
  if debut==year:groups.append('first_MLB_season')
  if debut==year-1:groups.append('second_MLB_season')
  if gp and 0<gs<gp:groups.append('swingmen')
  mi=milb(ident,debut) if debut else None
  if mi and debut>=year-3:groups.append('recent_debut_with_MiLB')
  if 2017<=year<=2023:groups.append('2020_in_workload_window' if year-3<=2020<=year else '2020_outside_window')
  cases.append({'mlbam_id':ident,'name':z['name'],'anchor':year,'target_year':year+1,'age':age,'role':rr,'debut_year':debut,'debut_MiLB_IP':mi,'groups':groups,'actual':target['stat'] if target else {},**{method:project(f[method],rr,age,year,True) for method in methods}})
 (OUT/'Chronological_Progress.json').write_text(json.dumps({'cases_completed':len(cases)}))
print('Chronological cases',len(cases),flush=True)
scores=score(cases,methods,['IP','K','ER','BB','H','QA3','SV','HLD'])
(OUT/'Debut_Chronological_Cases.json').write_text(json.dumps(cases,separators=(',',':')))
(OUT/'Debut_Chronological_Validation.json').write_text(json.dumps({'protocol':'Past-only caps and completed one-year training pairs; identities divisible by5 held out. Frozen early2010-2012 rate priors; anchors>=2016. Pandemic pairs excluded from training to avoid blind normalization. No fitting. This chronological companion is not byte-identical frozen V2.3C.','scores':scores,'methods':methods},indent=2))
# Re-score exact preserved94 cases against frozen original paths (explicit inherited leakage limitation).
held=json.loads((OUT/'Historical_Cases.json').read_text());paired=[]
for z in held:
 ident=z['mlbam_id'];year=z['anchor'];rows=hist[ident,'P'];rr=z['role'];pred={method:project(forecast(rows,rr,year,ident,method),rr,z['age'],year) for method in methods}
 assert max(abs(pred['baseline'].get(k,0)-z['baseline'].get(k,0)) for k in pred['baseline'])<1e-8
 paired.append(z|pred|{'groups':z['subgroups']})
(OUT/'Debut_Frozen94_Validation.json').write_text(json.dumps(score(paired,methods,['IP','K','ER','BB','H','QA3','SV','HLD']),indent=2))
# Every catalog pitcher receives an evidence audit; only debut rows within original window can alter forecasts.
ledger=inventory(catalog,v.cf.PROFILES);current=[];original=v.recent_forecast
for e in ledger:
 a=next(a for a in catalog['assets'] if a['id']==e['id']);p=old.players.get(e['id']);ident=e['mlbam_id'];rr=v.role(p) if p else None
 if not p or rr not in ['SP','RP']:continue
 rows=v.seasons(p,rr);base=original(p,rr)
 if not base:continue
 if ident and ident not in first and rows:first[ident]=min(z['year'] for z in rows)
 result={'id':e['id'],'name':e['name'],'owner':e['owner'],'age':p.get('age'),'role':rr,'debut_year':first.get(ident),'verified_debut_MiLB_IP':milb(ident,first[ident]) if ident in first else None,'baseline':pitching_projection(a['audit'],rr),'baseline_neutral':a['values']['neutral']['display'],'recent_MLB_seasons':[{'year':z['year'],'IP':z['stat'].get('IP'),'role':z['role']} for z in rows if z['year']>=2023]}
 for method in methods[1:]:
  f=forecast(rows,rr,2026,ident,method)
  if not f:continue
  assert max(abs(f[0][k]-base[0][k]) for k in f[0])<1e-12,(e['name'],'talent mismatch');assert abs(forecast(rows,rr,2026,ident)[1]-base[1])<1e-8
  if abs(f[1]-base[1])<1e-10:result[method]={'projection':result['baseline'],'neutral':result['baseline_neutral'],'IP_delta':0,'value_delta':0};continue
  def candidate(q,role,scenario='base'):
   out=original(q,role,scenario)
   if q['id']==p['id'] and role==rr and out:
    audit=copy.deepcopy(out[2]);audit['projected_workload']=f[1];return out[0],f[1],audit
   return out
  v.recent_forecast=candidate
  try:
   paths,audit=m.paths(p);proj=pitching_projection(audit,rr);value=m.competitive(paths,'neutral')['display']
  finally:v.recent_forecast=original
  result[method]={'projection':proj,'neutral':value,'IP_delta':proj.get('IP',0)-result['baseline'].get('IP',0),'value_delta':value-result['baseline_neutral'],'MLB_talent_rates_identical':True}
 current.append(result)
print('Current modeled pitchers',len(current),flush=True)
(OUT/'Debut_Current_Impact.json').write_text(json.dumps(current,indent=2))
csvrows=[]
for z in current:
 for method in methods[1:]:
  c=z.get(method)
  if not c or abs(c['IP_delta'])<1:continue
  csvrows.append({'id':z['id'],'player':z['name'],'fantasy_organization':z['owner'],'age':z['age'],'role':z['role'],'debut_year':z['debut_year'],'debut_MiLB_IP':z['verified_debut_MiLB_IP'],'method':method,**{f'baseline_{k}':z['baseline'].get(k) for k in ['IP','K','QA3']},**{f'candidate_{k}':c['projection'].get(k) for k in ['IP','K','QA3']},'baseline_value':z['baseline_neutral'],'candidate_value':c['neutral'],'reason':'Verified debut-season capacity; original four-year window and role retained','support':'See chronological subgroup validation; not approved for release','uncertainty':'MLB opportunity, future role, availability; affiliated sources only'})
with (OUT/'Debut_Material_Impact.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(csvrows[0]) if csvrows else ['player']);w.writeheader();w.writerows(csvrows)
# Shortened-season sensitivity, both hitters and pitchers; actual talent rates retained except omit-policy removes2020 evidence.
pandemic=[]
for (ident,stream),history in hist.items():
 if ident%5:continue
 for year in [2021,2022,2023]:
  z=lookup.get((ident,year,stream));age=r.age_at(ident,year)
  if not z or age is None or not math.isfinite(age) or not any(t['year']==2020 for t in history):continue
  rr=z['role'];fs={method:forecast(history,rr,year,ident,'baseline',True,method) for method in ['raw','omit','bounded_capacity']}
  if any(q is None for q in fs.values()):continue
  target=lookup.get((ident,year+1,stream));pandemic.append({'name':z['name'],'mlbam_id':ident,'anchor':year,'role':rr,'groups':['all',rr],'actual':target['stat'] if target else {},**{method:project(f,rr,age,year,True) for method,f in fs.items()}})
(OUT/'Pandemic_Validation.json').write_text(json.dumps({'scores':score(pandemic,['raw','omit','bounded_capacity'],['IP','PA','K','ER','BB','H','QA3']),'n':len(pandemic),'current_default_direct_2020_exposure':'None:2023-2026 window. Aging paths annualize2020 counts162/60 already; diagnostic career workload also annualizes. Raw2020 suppresses workload only in historical recent windows.','Matt_Olson':next({'projection':a['audit']['projection'],'recent_years':a['audit']['projection_audit']['recent_observed_years'],'preaging_PA':a['audit']['projection_audit']['projected_workload'],'2020_stats':[z['stat'] for z in a['career_profile']['seasons'] if z['year']==2020]} for a in catalog['assets'] if a['name']=='Matt Olson')},indent=2))
print('DONE',flush=True)

"""Quality revision: annual paths only; frozen labels/probabilities preserved."""
import prototype as old
import numpy as np,json,math,datetime,re,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
G=old.read(old.I/'game-inputs.json.gz');bios=G['bios'];AN=old.AN
# Original normalizers and utility preserved: no cross-role equalization.
score=old.score;floor=old.STRUCTURAL_FLOOR;T=old.T;utility=old.utility;DISPLAY=old.DISPLAY;MODES=old.MODES
lookup=old.lookup
REFERENCE={r:float(np.median([a["stat"].get("PA" if r=="H" else "IP",0) for a in old.cal if a["role"]==r])) for r in old.FULL}
def surplus(s,r):
 # Compare replacement over matching exposure; no full negative SP floor for a partial season.
 return score(s,r)-floor[r]*s.get("PA" if r=="H" else "IP",0)/REFERENCE[r]
ROLE_YEAR={}
for a in AN:
 k=(a['id'],a['year']);e=a['stat'].get('PA' if a['role']=='H' else 'IP',0)
 if k not in ROLE_YEAR or e>ROLE_YEAR[k]['stat'].get('PA' if ROLE_YEAR[k]['role']=='H' else 'IP',0):ROLE_YEAR[k]=a

def age_at(id,year):
 b=bios.get(str(id),{}).get('birthDate')
 try:return (datetime.date(year,6,30)-datetime.date.fromisoformat(b)).days/365.2425
 except (ValueError,TypeError):return None

def agebin(a):return 'under29' if a<29 else '29to32' if a<33 else '33to36' if a<37 else '37plus'
def exposure(s,r):return s.get('PA' if r=='H' else 'IP',0)
def identity(p):
 id=p.get('mlbamId')
 if not id:
  c=old.NAME_IDS.get(old.normalized_name(p['name']),set());id=next(iter(c)) if len(c)==1 else None
 return id
# Historical annual rate changes for observed active consecutive seasons; no holdout labels used.
aging={};pairs={}
for a in AN:
 r=a['role'];age=age_at(a['id'],a['year']);b=ROLE_YEAR.get((a['id'],a['year']+1));e=exposure(a['stat'],r)
 if age is None or not b or b['role']!=r or e<(250 if r=='H' else 60 if r=='SP' else 30):continue
 e2=exposure(b['stat'],r)
 if e2<(150 if r=='H' else 40 if r=='SP' else 20):continue
 key=(r,agebin(age));z=pairs.setdefault(key,[]);change={}
 for f in old.fields[r]:
  if f in ['IP','PA','AB']:continue
  ra=a['stat'].get(f,0)/e;rb=b['stat'].get(f,0)/e2
  change[f]=[ra,rb] # Include zero counts: avoid selecting a prior lucky season.
 z.append({'rate_changes':change,'workload':min(1.5,max(.4,e2/e))})
for r in old.FULL:
 aging[r]={}
 for bin in ['under29','29to32','33to36','37plus']:
  z=pairs.get((r,bin),[]);n=len(z);rates={}
  for f in old.fields[r]:
   vals=[x['rate_changes'][f] for x in z if f in x['rate_changes']];before=float(np.mean([v[0] for v in vals])) if vals else 0;after=float(np.mean([v[1] for v in vals])) if vals else 0;v=min(1.5,max(.5,after/before)) if before else 1;rates[f]=1+(v-1)*len(vals)/(len(vals)+30)
  work=float(np.median([x['workload'] for x in z])) if z else 1;aging[r][bin]={'n':n,'rates':rates,'workload_change':min(1.03,max(.90,1+(work-1)*n/(n+30)))}

def forecast(p,r):
 id=identity(p);rows=[]
 for y,w in [(2023,.1),(2024,.2),(2025,.3)]:
  a=ROLE_YEAR.get((id,y))
  if a and a['role']==r and exposure(a['stat'],r)>0:rows.append((a['stat'],w,y))
 cur=old.current(p,r)
 if exposure(cur,r)>0:rows.append((cur,.4,2026))
 if not rows:return None
 mass=sum(w for s,w,y in rows);rows=[(s,w/mass,y) for s,w,y in rows];recent=sum(exposure(s,r)*w for s,w,y in rows);healthy=float(np.median(sorted([exposure(s,r) for s,w,y in rows],reverse=True)[:2]));work=.70*recent+.30*healthy
 # Role prior exposure is inferred from observed regular-workload historical seasons, not a fixed hard cap.
 prior_work=float(np.median([exposure(a['stat'],r) for a in old.cal if a['role']==r]));n=len(rows);priorweight=1/(n+3);work=(1-priorweight)*work+priorweight*prior_work
 cap=float(np.quantile([exposure(a['stat'],r) for a in AN if a['role']==r and exposure(a['stat'],r)>0],.98));work=min(work,cap)
 strength=100 if r=='H' else 30;rates={f:(sum(s.get(f,0)*w for s,w,y in rows)+strength*old.prior[r][f])/(recent+strength) for f in old.fields[r]}
 return rates,work,{'id':id,'observed_years':[y for s,w,y in rows],'recent_workload':recent,'healthy_observed_workload':healthy,'role_workload_prior':prior_work,'projected_workload':work,'prior_weight':priorweight,'flags':['Observed-season estimates omit pre-debut zero seasons','Workload recovery weight .30 and shrinkage are provisional; missing current exposure broadens uncertainty','Historical aging is conditioned on active survivors; attrition remains in scenario risk']}

# Development-only empirical eight-year paths retain zero seasons, arrivals, workload loss and role changes.
# First ranking <=2015 implies complete eight-year follow-up through2022, before final 2020 holdout labels end.
career={r:{c:[] for c in range(5)} for r in ['H','SP']};arrival={r:[] for r in ['H','SP']}
for a in old.CO:
 r='SP' if a['pitcher'] else 'H';path=[];arr=None
 for t in range(8):
  b=ROLE_YEAR.get((a['mlbamId'],a['year']+t));value=max(0,surplus(b['stat'],b['role'])) if b else 0;path.append(value)
  if arr is None and b and exposure(b['stat'],b['role'])>=(250 if r=='H' else 40):arr=t
 # Align profiles to first regular exposure for player-specific ETA. Labels remain exact old5-year classes.
 aligned=[]
 for offset in range(8):
  yr=a['year']+arr+offset if arr is not None else None
  b=ROLE_YEAR.get((a['mlbamId'],yr)) if yr is not None else None
  aligned.append(None if yr is not None and yr>2025 else (max(0,surplus(b['stat'],b['role'])) if b else 0.))
 career[r][a['five_year_label']].append({'id':a['mlbamId'],'rank_year':a['year'],'arrival_lag':arr,'rank_path':path,'arrival_path':aligned})
 if arr is not None:arrival[r].append(arr)

# Right-censored post-arrival years borrow observed same-class trajectory means, not zeros or peaks.
for r in career:
 for c,samples in career[r].items():
  for offset in range(8):
   observed=[a['arrival_path'][offset] for a in samples if a['arrival_path'][offset] is not None]
   pooled=[a['arrival_path'][offset] for rr in career for a in career[rr][c] if a['arrival_path'][offset] is not None]
   estimate=float(np.mean(observed or pooled)) if observed or pooled else 0.
   for a in samples:
    if a['arrival_path'][offset] is None:a['arrival_path'][offset]=estimate

def prospect_paths(p,scenario='base'):

 r=old.role(p);family='SP' if r!='H' else 'H';rank=float(p['prospect'].get('rank') or 350);age=float(p.get('age') or 23);pr=old.probabilities(rank,age,int(family=='SP'));etamatch=re.search(r'20\d\d',str(p['prospect'].get('eta') or ''));eta=int(etamatch.group()) if etamatch else 2027+int(round(np.median(arrival[family]))); eta+=1 if scenario=='low' else -1 if scenario=='high' else 0
 result=[];samplecounts={};mul=.80 if scenario=='low' else 1.20 if scenario=='high' else 1
 for c in range(5):
  samples=career[family][c];samplecounts[c]=len(samples)
  if c and len(samples)<5:samples=career['H'][c]+career['SP'][c]
  if not samples:samples=[{'arrival_path':[0.]*8}]
  for a in samples:
   # Explicit late maturation remains possible even for frozen class0. No second bust discount.
   path=[]
   for t in range(8):
    offset=2027+t-eta
    s=a['arrival_path'][offset]*mul if 0<=offset<8 else 0
    path.append(utility(s))
   result.append((float(pr[c])/len(samples),path))
 return result,{'kind':'prospect','role':r,'probabilities':pr.tolist(),'eta':eta,'class_path_counts':samplecounts,'flags':['Empirical development-only annual paths; no sustainable two-peak-season assumption','Player ETA alignment is provisional; no extra upside bonus','Only2 development superstars; pooled tail paths remain fragile','Frozen5-year class0 can contain later8-year production','Pipeline-to-FanGraphs rank transfer remains unvalidated']}

def mlb_paths(p,scenario='base'):
 r=old.role(p);f=forecast(p,r)
 if not f:return None,None
 rates,work,audit=f;age=float(p.get('age') or 26);out=[]
 # Availability/production states are aggregate paths, not individual future injury calendars.
 q=.85 if scenario=='low' else 1.15 if scenario=='high' else 1
 state=[(.55,.2),(1,.6),(1.20,.2)] if r=='H' else [(.40,.25),(1,.55),(1.20,.20)]
 for factor,prob in state:
  rt=rates.copy();w=work;vals=[]
  for t in range(8):
   if t:
    ag=aging[r][agebin(age+t)];w*=ag['workload_change']
    rt={k:v*ag['rates'].get(k,1) for k,v in rt.items()}
   s={k:v*w*factor*q for k,v in rt.items()}
   if r=='H':
    s['H']=min(s['H'],s['AB']);s['HR']=min(s['HR'],s['H']);s['TB']=min(4*s['AB'],max(s['H'],s['TB']))
   else:s['QA3']=min(s['QA3'],s['IP']/5)
   vals.append(utility(surplus(s,r)))
  out.append((prob,vals))
 if len(audit['observed_years'])<=2:audit['flags'].append('Short MLB history: no dated individual prospect prior in reviewed inputs; historical role-rate shrinkage applies and transition mixture awaits that evidence')
 return out,{'kind':'MLB','role':r,'projection':{k:v*work for k,v in rates.items()},'projection_audit':audit,'flags':['Aggregate uncertainty states provisional','Aging derived from observed consecutive seasons; survivor bias persists','35IP is a team constraint, no individual future weekly bonus']}

def player_paths(p,scenario='base'):
 mlb,ma=mlb_paths(p,scenario);pros,pa=prospect_paths(p,scenario) if p.get('prospect') else (None,None)
 if mlb and pros:
  r=old.role(p);id=identity(p);e=sum(exposure(a['stat'],r) for a in AN if a['id']==id and a['role']==r)+exposure(old.current(p,r),r);strength=600 if r=='H' else 170;w=e/(e+strength)
  # Reliability mixture: weights sum1, actual MLB evidence smoothly replaces prior.
  return [(prob*w,v) for prob,v in mlb]+[(prob*(1-w),v) for prob,v in pros],{'kind':'hybrid','role':r,'MLB_reliability':w,'career_MLB_exposure':e,'MLB':ma,'prospect':pa,'flags':['Smooth empirical-evidence mixture, not an abrupt threshold','600PA/170IP reliability strengths provisional; not a posterior fitted likelihood']}
 if mlb:return mlb,ma
 if pros:return pros,pa
 return [(1,[0.]*8)],{'kind':'unmodeled','role':old.role(p),'flags':['Insufficient evidence; no zero-price inference']}

# Draft availability: sequential Plackett-Luce preference draws, not deterministic round bins.
DRAFT=old.ordered;RNG=np.random.default_rng(8082026);draft_weights=np.zeros((60,len(DRAFT)));runs=1200
for j in range(runs):
 # Exponential race samples without replacement with preference around ranked order.
 noise=RNG.exponential(1,size=len(DRAFT));pref=np.exp(-np.arange(len(DRAFT))/8);order=np.argsort(noise/pref)
 for slot,idx in enumerate(order[:60]):draft_weights[slot,idx]+=1/runs

def pick_paths(p,scenario='base'):
 round=int(p['round']);slot=int(p['slot'])
 if not 1<=round<=5 or not 1<=slot<=12:raise ValueError('Tradable picks must be rounds1–5, slots1–12')
 overall=(round-1)*12+slot;ps=[];avail=[];year=p['year']
 for index,chance in enumerate(draft_weights[overall-1]):
  if chance==0:continue
  d=DRAFT[index];rank=float(d.get('sourceRanks',{}).get('ddOverall') or 100+5*d['pipelineRank']);rank*=1.35 if scenario=='low' else .75 if scenario=='high' else 1
  eta=year+(2 if float(d.get('age') or 20)>=21 else 3)
  proxy={'name':d['name'],'position':'SP' if d.get('type')=='P' else d.get('position','SS'),'age':float(d.get('age') or 20),'prospect':{'rank':rank,'eta':str(eta)},'bat':{},'pit':{}}
  paths,audit=prospect_paths(proxy,scenario);ps.extend((prob*chance,v) for prob,v in paths)
  avail.append({'name':d['name'],'selection_probability':float(chance),'available_before_probability':float(1-draft_weights[:overall-1,index].sum()),'rank_proxy':rank})
 return ps,{'kind':'pick','role':'mixture','year':year,'round':round,'slot':slot,'overall':overall,'availability':sorted(avail,key=lambda x:-x['selection_probability'])[:12],'flags':['Sequential preference model,1200 seeded drafts; preference spread8 is provisional','Actual historical league draft order/preferences unavailable','Specific selection known; future class uses2026 candidate proxy','Only rounds1–5 are tradable; no assets for6–20']}

def evaluate_paths(ps,mode):
 pr=np.array([prob for prob,v in ps]);arr=np.array([v for prob,v in ps]);w=old.weights(mode);vals=np.sum(arr*w,axis=1);mean=float(np.sum(pr*vals));sd=float(np.sqrt(np.sum(pr*(vals-mean)**2)));penalty={'neutral':0,'contender':.10,'balanced':.04,'rebuild':0}[mode]*sd
 return {'underlying':max(0,mean-penalty),'expected_before_risk_preference':mean,'outcome_dispersion':sd,'risk_preference_deduction':penalty,'display':DISPLAY*max(0,mean-penalty)}

def value(p,scenario='base'):
 ps,audit=pick_paths(p,scenario) if p.get('kind')=='pick' else player_paths(p,scenario)
 values={m:evaluate_paths(ps,m) for m in MODES}
 if audit['kind']=='unmodeled':values={m:{'display':None,'underlying':None} for m in MODES}
 return {'id':p['id'],'name':p['name'],'audit':audit,'values':values,'annual_expected_utility':[sum(pr*v[t] for pr,v in ps) for t in range(8)]}

def build():
 catalog=[];errors=[]
 for p in old.players.values():
  a=value(p)
  if a['audit']['kind']=='unmodeled':continue
  a['range']={s:{m:x['display'] for m,x in value(p,s)['values'].items()} for s in ['low','high']};catalog.append(a)
 # UI exposes specific slots, not unconfirmed owner-to-slot assignments.
 for year in [2027,2028,2029]:
  for r in range(1,6):
   for slot in range(1,13):
    p={'id':f'slot-{year}-{r}-{slot}','name':f'{year} {r}.{slot:02d}','kind':'pick','year':year,'round':r,'slot':slot};a=value(p);a['range']={s:{m:x['display'] for m,x in value(p,s)['values'].items()} for s in ['low','high']};catalog.append(a)
 by={a['id']:a for a in catalog}
 for p in old.picks.values():
  if not 1<=p['round']<=5:continue
  samples=[by[f"slot-{p['year']}-{p['round']}-{s}"] for s in range(1,13)]
  a={'id':p['id'],'name':p['name']+' (slot unknown)','audit':{'kind':'pick','year':p['year'],'round':p['round'],'slot':None,'flags':['Historical owner pick slot unverified:12-slot marginal mean, not a specific selection']},'values':{m:{'display':float(np.mean([x['values'][m]['display'] for x in samples])),'underlying':float(np.mean([x['values'][m]['underlying'] for x in samples]))} for m in MODES},'range':{s:{m:float(min(x['range'][s][m] for x in samples) if s=='low' else max(x['range'][s][m] for x in samples)) for m in MODES} for s in ['low','high']},'annual_expected_utility':np.mean([x['annual_expected_utility'] for x in samples],axis=0).tolist()};catalog.append(a);by[a['id']]=a
 trades=[]
 for c in old.U2['cases'][:4]:
  modes={}
  for mode in MODES:
   totals=[];bounds=[]
   for ids in c['identities']:
    v=0;lo=0;hi=0
    for id in ids:
     if id in by:
      a=by[id];v+=a['values'][mode]['display'];lo+=min(a['range']['low'][mode],a['range']['high'][mode]);hi+=max(a['range']['low'][mode],a['range']['high'][mode])
     else:
      p=old.picks[id];samples=[by[f"slot-{p['year']}-{p['round']}-{s}"] for s in range(1,13)];v+=np.mean([a['values'][mode]['display'] for a in samples]);lo+=min(a['range']['low'][mode] for a in samples);hi+=max(a['range']['high'][mode] for a in samples)
    totals.append(float(v));bounds.append([float(lo),float(hi)])
   modes[mode]={'package_values':totals,'net_first_owner':totals[1]-totals[0],'assumption_range':[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]],'U2_original_net':c['comparisons'][mode]['B']['net'][0]}
  trades.append({'id':c['id'],'teams':c['teams'],'sends':c['sends'],'identities':c['identities'],'modes':modes,'warning':'NOW stress; historical pick slots unknown, marginalized over12 possibilities; no fairness fitting'})
 old.write('revised_results.json',{'assets':catalog,'trades':trades,'aging':aging,'career_path_sample_counts':{r:{c:len(s) for c,s in cs.items()} for r,cs in career.items()},'draft_model':{'runs':runs,'seed':8082026,'preference_spread':8},'production':'unchanged; isolated preview only'})
 print('Revised catalog',len(catalog),'assets; four trades saved')
if __name__=='__main__':build()

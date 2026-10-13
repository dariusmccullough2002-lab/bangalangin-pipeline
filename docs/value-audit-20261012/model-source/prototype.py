"""Offline long-term dynasty prototype. Never writes to production or old research."""
import json,gzip,math,re,hashlib,statistics,unicodedata
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;I=P/'inputs'
def read(f):return json.load(gzip.open(f,'rt') if str(f).endswith('.gz') else open(f))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
def ip(x):
 a,b=(str(x or 0).split('.')+['0'])[:2];return int(a)+int(b[:1] or 0)/3

def role(p):return 'SP' if 'SP' in p.get('position','') or p.get('pit',{}).get('GS',0)>=5 else 'RP' if p.get('pit') else 'H'
def vector(s,r,refs):
 if r=='H':
  ab=s.get('AB',0);den=ab+s.get('BB',0)+s.get('HBP',0)+s.get('SF',0);ops=(s.get('H',0)+s.get('BB',0)+s.get('HBP',0))/den+s.get('TB',0)/ab if ab and den else 0
  return np.array([s.get(k,0) for k in ['HR','R','RBI','SB']]+[s.get('H',0)-refs['AVG']*ab,(ops-refs['OPS'])*ab])
 return np.array([-s.get('ER',0),s.get('K',0),3*s.get('SV',0)+2*s.get('HLD',0),s.get('QA3',0),s.get('K',0)-refs['KBB']*s.get('BB',0),refs['WHIP']*s.get('IP',0)-s.get('H',0)-s.get('BB',0)])

def collect_cached_seasons():
 # Read cached official inputs only; no networking and no original script execution.
 old=Path('/workspace/scratch/1a661c5d6ceb/phase1-calibration/raw');new=Path('/workspace/scratch/1a661c5d6ceb/foundational-calibration/raw');games=read(I/'game-inputs.json.gz');rows=[]
 for year in range(2010,2026):
  for group in ['hitting','pitching']:
   f=old/f'{group}-{year}.json';f=f if f.exists() else new/f'mlb-{group}-{year}.json.gz'
   for ss in read(f)['stats']:
    for a in ss['splits']:
     s=a['stat'];id=a['player']['id'];r='H' if group=='hitting' else 'SP' if float(s.get('gamesStarted',0))>=5 else 'RP'
     fields={'AB':'atBats','PA':'plateAppearances','H':'hits','HR':'homeRuns','R':'runs','RBI':'rbi','SB':'stolenBases','BB':'baseOnBalls','HBP':'hitByPitch','SF':'sacFlies','TB':'totalBases'} if r=='H' else {'K':'strikeOuts','ER':'earnedRuns','SV':'saves','HLD':'holds','H':'hits','BB':'baseOnBalls'}
     z={k:float(s.get(v,0) or 0) for k,v in fields.items()}
     if r!='H':z['IP']=ip(s.get('inningsPitched'));z['QA3']=games['annual_QA3'].get(str(year),{}).get(str(id),{}).get('QA3',0)
     rows.append({'id':id,'year':year,'role':r,'name':a['player']['fullName'],'stat':z})
 write('inputs/annual-components.json',rows)
 return rows

DB=read(I/'baseline.json.gz');U2=read(I/'u2_results.json');FREEZE=read(I/'trained-model-freeze.json')['models']['expanded_core'];CO=read(I/'delayed-arrival-diagnostic.json');DRAFT=read(I/'draft.json')['players']
AN=read(I/'annual-components.json') if (I/'annual-components.json').exists() else collect_cached_seasons()
players={p['id']:p for p in DB['players']};picks={p['id']:p for p in DB['picks']};lookup={(r['year'],r['id'],r['role']):r for r in AN}
def normalized_name(n):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower())
NAME_IDS={}
for a in AN:NAME_IDS.setdefault(normalized_name(a['name']),set()).add(a['id'])
for e in read(I/'free-prospect-cohort.json'):
 if e['fantraxId'] in players and not players[e['fantraxId']].get('prospect'):
  players[e['fantraxId']]['prospect']={'rank':e['external_rank'],'eta':str(e['eta']),'provider':'FanGraphs dated 2026-07-23 free-agent cohort'}
  players[e['fantraxId']]['mlbamId']=e['mlbamId']
QUAL=lambda r:r['stat'].get('AB',0)>=250 if r['role']=='H' else r['stat'].get('IP',0)>=(80 if r['role']=='SP' else 30)
cal=[r for r in AN if r['year']<=2012 and QUAL(r)]
h=[r['stat'] for r in cal if r['role']=='H'];p=[r['stat'] for r in cal if r['role']!='H'];total=lambda rows,k:sum(s.get(k,0) for s in rows)
refs={'AVG':total(h,'H')/total(h,'AB'),'OPS':(total(h,'H')+total(h,'BB')+total(h,'HBP'))/(total(h,'AB')+total(h,'BB')+total(h,'HBP')+total(h,'SF'))+total(h,'TB')/total(h,'AB'),'KBB':total(p,'K')/total(p,'BB'),'WHIP':(total(p,'H')+total(p,'BB'))/total(p,'IP')}
dens={f:np.maximum(.01,np.std([vector(r['stat'],r['role'],refs) for r in cal if ('H' if r['role']=='H' else 'P')==f],axis=0)) for f in ['H','P']}
def score(s,r):return float(np.sum(vector(s,r,refs)/dens['H' if r=='H' else 'P']))
floor={r:float(np.quantile([score(a['stat'],r) for a in cal if a['role']==r],.3)) for r in ['H','SP','RP']}
STRUCTURAL_FLOOR=floor.copy()
def surplus(s,r,depth=1):return score(s,r)-floor[r]-(depth-1)*T
T=max(.1,float(np.quantile([max(0,score(a['stat'],a['role'])-floor[a['role']]) for a in cal],.9)))
def utility(s,curve=.1):return max(0,s)+curve*max(0,s-T)**2/T
MODES=['neutral','contender','balanced','rebuild'];HORIZON=8
DISPLAY=100/(utility(T)*sum(.88**t for t in range(HORIZON)))
def weights(mode,discount=.88):
 w=np.array([discount**t for t in range(HORIZON)]);z=np.array([3,1.5,.7,.25,.25,.25,.25,.25]) if mode=='contender' else np.array([.2,.5,1.2,1.2,1.2,1.2,1.2,1.2]) if mode=='rebuild' else np.array([1.2,1.2,1.2,.85,.85,.85,.85,.85]) if mode=='balanced' else np.ones(8)
 return w*z*sum(w)/sum(w*z)
# Crosswalk uses development identities only, never final 2020 outcomes.
class_samples={r:{c:[] for c in range(5)} for r in ['H','SP','RP']}
for a in CO:
 r='H' if not a['pitcher'] else 'SP';vals=[]
 for y in range(a['year'],a['year']+5):
  b=lookup.get((y,a['mlbamId'],r))
  if r=='SP' and not b:b=lookup.get((y,a['mlbamId'],'RP'))
  vals.append(max(0,surplus(b['stat'],b['role'])) if b else 0)
 # Class label itself is inherited unchanged. This peak-to-path mapping is provisional.
 class_samples[r][a['five_year_label']].append(sum(sorted(vals,reverse=True)[:2])/2)
anchors={};counts={}
for r in ['H','SP','RP']:
 anchors[r]=[0];counts[r]=[len(class_samples[r][0])]
 for c in range(1,5):
  pooled=class_samples['H'][c]+class_samples['SP'][c];own=class_samples[r][c];n=len(own);v=float(np.median(pooled)) if pooled else 0
  anchors[r].append((n/(n+10))*float(np.median(own))+(10/(n+10))*v if own else v);counts[r].append(n)
# All RP prospect outcomes borrow pooled anchors; explicitly unsupported role transition.
def probabilities(rank,age,pitch):
 effective=max(1,min(100,rank));x=np.array([math.log(effective),age,pitch]);x=(x-np.array(FREEZE['scaler_mean']))/np.array(FREEZE['scaler_scale']);z=np.array(FREEZE['coef'])@x+np.array(FREEZE['intercept']);z-=max(z);pr=np.exp(z);pr/=sum(pr)
 if rank>100:
  # Rank extrapolation is a transparent reach attenuation, not a fitted tail claim.
  pr[1:]*=100/rank;pr[0]=1-sum(pr[1:])
 return pr
FULL={'H':600,'SP':170,'RP':65}
fields={'H':['AB','PA','H','HR','R','RBI','SB','BB','HBP','SF','TB'],'SP':['IP','K','ER','SV','HLD','QA3','H','BB'],'RP':['IP','K','ER','SV','HLD','QA3','H','BB']}
prior={r:{k:total([a['stat'] for a in cal if a['role']==r],k)/total([a['stat'] for a in cal if a['role']==r],'PA' if r=='H' else 'IP') for k in fields[r]} for r in FULL}
def current(p,r):
 s=p.get('bat' if r=='H' else 'pit',{}).copy()
 if r!='H':s['IP']=ip(s.get('IP'));s['QA3']=float(s.get('QA3',0))
 return s

def forecast(p,r):
 hist=[]
 mlbam=p.get('mlbamId')
 if not mlbam:
  def norm(n):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower())
  candidates=NAME_IDS.get(normalized_name(p['name']),set())
  if len(candidates)==1:mlbam=next(iter(candidates))
 for y,w in [(2023,.1),(2024,.2),(2025,.3)]:
  a=lookup.get((y,mlbam,r))
  if mlbam:hist.append((a['stat'] if a else {},w))
 if p.get('bat' if r=='H' else 'pit'):hist.append((current(p,r),.4))
 if not hist or not any(s.get('PA' if r=='H' else 'IP',0)>0 for s,w in hist):return None
 z=sum(w for s,w in hist);hist=[(s,w/z) for s,w in hist];e='PA' if r=='H' else 'IP';ex=sum(s.get(e,0)*w for s,w in hist);strength=100 if r=='H' else 30
 rates={k:(sum(s.get(k,0)*w for s,w in hist)+strength*prior[r][k])/(ex+strength) for k in fields[r]};work=min(FULL[r],ex)
 return {k:rates[k]*work for k in fields[r]}, {'source':'Cached official 2023–2025 plus supplied 2026 export; regression forecast, not external projection','weighted_exposure':ex,'projected_exposure':work,'years_available':len(hist),'mlbamId':mlbam,'identity_method':'snapshot MLBAM or unique normalized official name; ambiguous names not resolved'}
SCENARIOS={'low':{'production':.8,'replacement':1.15,'eta':1,'crosswalk':.75},'base':{'production':1,'replacement':1,'eta':0,'crosswalk':1},'high':{'production':1.2,'replacement':.85,'eta':-1,'crosswalk':1.25}}
def paths(p,scenario='base',curve=.1):
 r=role(p);age=float(p.get('age') or 26);q=SCENARIOS[scenario];proj=forecast(p,r);ex=current(p,r).get('PA' if r=='H' else 'IP',0);ispros=bool(p.get('prospect')) and ex<(250 if r=='H' else 100)
 if ispros:
  rank=float(p['prospect'].get('rank') or 350);pr=probabilities(rank,age,int(r!='H'));eta=int(re.search(r'20\d\d',p['prospect'].get('eta','2030')).group())+q['eta'];out=[]
  for c,a in enumerate(anchors[r]):
   v=[]
   for t in range(8):
    year=2027+t; ramp=max(0,min(1,(year-eta+1)/2));agefactor=math.exp(-(.045 if r=='H' else .07)*max(0,age+t-29))
    # Bust risk lives in pr[0], never apply another success/bust discount.
    s=max(0,a*q['crosswalk']+STRUCTURAL_FLOOR[r]-floor[r]-(q['replacement']-1)*T) if c else 0
    v.append(utility(s*ramp*agefactor,curve))
   out.append((float(pr[c]),v))
  flags=['Provisional class-to-QA3 contribution crosswalk and peak-to-eight-year path','Pipeline ranks not matched to historical provider','ETA and aging are assumptions','Five-year superstar probability remains weakly identified']
  if rank>100:flags+=['Rank beyond trained top100: provisional attenuation']
  if r=='RP':flags+=['RP class path borrowed from pooled development outcomes']
  return out,{'kind':'prospect','role':r,'rank':rank,'probabilities':pr.tolist(),'eta':eta,'flags':flags}
 if proj is None:return [(1.,[0.]*8)],{'kind':'unmodeled','role':r,'flags':['Missing MLB/prospect evidence; zero is unknown, not a measured worthless asset']}
 s,audit=proj;out=[]
 # Scenario states represent persistent production/availability uncertainty, not individual injury schedules.
 for factor,prob in [(.6,.2),(1,.6),(1.25,.2)]:
  vals=[]
  for t in range(8):
   aging=math.exp(-(.045 if r=='H' else .07)*max(0,age+t-29));workfade=math.exp(-(.02 if r=='H' else .035)*t)
   z={k:v*factor*q['production']*workfade for k,v in s.items()};ratekeys=['H','HR','R','RBI','SB','TB'] if r=='H' else ['K','QA3','SV','HLD'];
   for k in ratekeys:z[k]*=aging
   vals.append(utility(surplus(z,r,q['replacement']),curve))
  out.append((prob,vals))
 return out,{'kind':'MLB','role':r,'forecast_components':s,'forecast_audit':audit,'flags':['Projection, aging and persistent production-state weights are provisional','Rate residuals approximate team ratio impact; not exact matchup wins']}

def evaluate_paths(ps,mode):
 w=weights(mode);values=np.array([float(np.dot(w,v)) for pr,v in ps]);pr=np.array([pr for pr,v in ps]);mean=float(pr@values);sd=float(np.sqrt(pr@((values-mean)**2)));penalty={'neutral':0,'contender':.10,'balanced':.04,'rebuild':0}[mode]*sd
 return {'underlying':max(0,mean-penalty),'expected_before_risk_preference':mean,'outcome_dispersion':sd,'risk_preference_deduction':penalty,'display':DISPLAY*max(0,mean-penalty)}
ordered=sorted([d for d in DRAFT if d.get('draftYear')==2026 and d.get('pipelineRank')],key=lambda d:d['pipelineRank'])
def pick_paths(p,scenario='base',curve=.1):
 if p['round'] not in range(1,6):raise ValueError('Only rounds1–5 are tradable')
 start=(p['round']-1)*12;end=p['round']*12;pool=ordered[start:end]
 if len(pool)!=12:raise ValueError('Insufficient draft candidates for this round')
 ps=[];names=[]
 for d in pool:
  rank=d.get('sourceRanks',{}).get('ddOverall');fallback=not rank
  rank=float(rank or (100+5*d['pipelineRank']));rank*=1.4 if scenario=='low' else .75 if scenario=='high' else 1
  eta=p['year']+(2 if d.get('age',20)>=21 else 3);q={'name':d['name'],'age':float(d.get('age') or 20),'position':'SP' if d.get('type')=='P' else d.get('position','SS'),'prospect':{'rank':rank,'eta':str(eta)},'bat':{},'pit':{}}
  sub,audit=paths(q,scenario,curve);ps.extend((prob/len(pool),v) for prob,v in sub);names.append({'name':d['name'],'rank_proxy':rank,'fallback_rank':fallback})
 return ps,{'kind':'pick','role':'mixture','year':p['year'],'round':p['round'],'candidates':names,'flags':['Equal probability over candidate order within round; actual selection preference and pool not fitted','Dynasty Dugout overall rank cross-provider transfer is unvalidated; fallback mapping is illustrative','2028/2029 use current class as proxy, not known future class','12 teams; no standalone value for rounds6–20']}

def asset(p,scenario='base',curve=.1):
 ps,audit=pick_paths(p,scenario,curve) if p.get('kind')=='pick' else paths(p,scenario,curve)
 result={'id':p['id'],'name':p['name'],'audit':audit,'values':{m:evaluate_paths(ps,m) for m in MODES}}
 if audit['kind']=='unmodeled':result['values']={m:{'underlying':None,'display':None,'status':'insufficient evidence'} for m in MODES}
 return result

def capacity(give,receive,open_slots=None,drop_values=None):
 delta=sum(p.get('kind')!='pick' for p in receive)-sum(p.get('kind')!='pick' for p in give)
 if open_slots is None:return {'adjustment':0,'status':'unknown roster openings; no automatic slot bonus/penalty','immediate_net_players':delta,'future_pick_obligations':sum(p.get('kind')=='pick' for p in receive)-sum(p.get('kind')=='pick' for p in give)}
 forced=max(0,delta-open_slots)
 if forced and (drop_values is None or len(drop_values)<forced):raise ValueError('Forced drops require eligible drop values')
 return {'adjustment':-sum(sorted(drop_values or [])[:forced]),'forced_drops':forced,'status':'supplied legal same-slot drop candidates; illustrative unless verified'}

def main():
 cs=U2['cases'][:4];selected={i for c in cs for side in c['identities'] for i in side}
 for name in ['Aaron Judge','Tarik Skubal','Emmanuel Clase','Tyson Hardin','Josh Naylor']:
  selected.update(p['id'] for p in players.values() if p['name']==name)
 assets={i:players.get(i,picks.get(i)) for i in selected};results={i:asset(p) for i,p in assets.items()};ranges={i:{s:asset(p,s) for s in ['low','high']} for i,p in assets.items()};comparisons=[]
 for c in cs:
  sides=c['identities'];objects=[[assets[i] for i in side] for side in sides];modes={}
  for m in MODES:
   totals=[sum(results[i]['values'][m]['display'] for i in side) for side in sides];net=[totals[1]-totals[0],totals[0]-totals[1]];sens=[]
   for s in ['low','high']:
    ts=[sum(ranges[i][s]['values'][m]['display'] for i in side) for side in sides];sens.append(ts[1]-ts[0])
   # Opposing-side envelope: low incoming/high outgoing and reverse; broader than same-assumption sensitivity.
   lo=sum(ranges[i]['low']['values'][m]['display'] for i in sides[1])-sum(ranges[i]['high']['values'][m]['display'] for i in sides[0]);hi=sum(ranges[i]['high']['values'][m]['display'] for i in sides[1])-sum(ranges[i]['low']['values'][m]['display'] for i in sides[0]);u2=c['comparisons'][m]['B'];modes[m]={'package_display':totals,'net_first_owner':net[0],'opposing_assumption_envelope':[min(lo,hi,net[0]),max(lo,hi,net[0])],'same_assumption_sensitivity':sens,'U2_original_net_first_owner':u2['net'][0],'U2_unit_warning':'U2 original numbers have a different scale and capacity rule; compare direction, not magnitude'}
  comparisons.append({'id':c['id'],'teams':c['teams'],'sends':c['sends'],'label':'NOW on preserved 2026-10-07 inputs; neither THEN nor REALIZED; not a fairness target','modes':modes,'capacity':[capacity(objects[0],objects[1]),capacity(objects[1],objects[0])]})
 fa=[]
 for p in players.values():
  if p.get('owner')=='Free agent' and (current(p,role(p)).get('PA',0)>=150 if role(p)=='H' else current(p,role(p)).get('IP',0)>=30):
   a=asset(p);fa.append({'id':p['id'],'name':p['name'],'role':role(p),'display':a['values']['neutral']['display'],'source':'2026-10-07 saved snapshot; not refreshed availability'})
 alternatives={r:sorted([a for a in fa if a['role']==r],key=lambda a:a['display'],reverse=True)[:10] for r in FULL}
 invariants={'probabilities_sum_one':all(abs(sum(prob for prob,v in (pick_paths(p) if p.get('kind')=='pick' else paths(p))[0])-1)<1e-9 for p in assets.values()),'constant_paths_equal_time_mass':max(sum(weights(m)) for m in MODES)-min(sum(weights(m)) for m in MODES)<1e-9,'convex_upside':.5*utility(0)+.5*utility(2*T)>utility(T),'expected_utility_not_utility_expected':evaluate_paths([(.5,[0.]*8),(.5,[utility(2*T)]*8)],'neutral')['underlying']>evaluate_paths([(1,[utility(T)]*8)],'neutral')['underlying'],'SP_RP_share_dispersion':all(np.allclose(vector(a['stat'],'SP',refs)/dens['P'],vector(a['stat'],'RP',refs)/dens['P']) for a in cal if a['role']=='SP'),'no_research_final_labels_used_for_crosswalk':all(a['year']<=2015 for a in CO),'capacity_zero_without_evidence':capacity([],[])['adjustment']==0,'forced_drop_actual_opportunity_cost':capacity([],list(players.values())[:3],1,[4,7])['adjustment']==-11,'linear_display_package_additive':abs(DISPLAY*sum([1,2])-sum(DISPLAY*x for x in [1,2]))<1e-9,'round6_rejected':False}
 try:pick_paths({'round':6,'year':2027})
 except ValueError:invariants['round6_rejected']=True
 invariants={k:bool(v) for k,v in invariants.items()}
 assert all(invariants.values()),invariants
 audit={'checkpoint':'9743a4af0b5c8a661ec567d724907d85cad3cab3','as_of':DB['asOf'],'horizon':list(range(2027,2035)),'references':refs,'dispersion':{k:v.tolist() for k,v in dens.items()},'replacement_floor':floor,'elite_threshold':T,'display_multiplier':DISPLAY,'class_anchors':anchors,'class_anchor_sample_counts':counts,'category_units':'sum annual signed count and ratio-impact / historical category dispersion; not wins','eligibility':'35IP per7days preserved as diagnostic; annual asset values assume an otherwise legal team; no projected weekly gate bonus','free_agent_snapshot':alternatives,'scarcity_adjustment':0,'scenarios':SCENARIOS,'warning':'All ranges are assumption envelopes of expected utility, not calibrated confidence intervals'}
 write('results.json',{'audit':audit,'assets':list(results.values()),'scenario_assets':ranges,'trades':comparisons,'invariants':invariants})
 write('input_hashes.json',{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in I.iterdir() if f.is_file()})
 print(json.dumps({'invariants':invariants,'anchors':anchors,'replacement':floor,'threshold':T,'trades':[{ 'id':c['id'],'net':{m:round(c['modes'][m]['net_first_owner'],1) for m in MODES}} for c in comparisons]},indent=2))
if __name__=='__main__':main()

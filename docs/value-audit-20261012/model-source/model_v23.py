"""Bounded V2.3 overlay. Never writes V2.2. Cached inputs and fixed common scale."""
from pathlib import Path
import sys,json,copy,functools,math
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path.insert(0,str(ROOT/'trade-preview-v22/model'));import model_v22 as base
r=base.r;old=base.old;cf=base.cf
CONFIG_PATH=P/'Selection.json'
CONFIG=json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {'hitter_reconciliation':'fixed_PA','leverage_policy':'no_growth'}
# GP/GS from cached official seasons; identity + season joins, never names.
@functools.lru_cache(None)
def appearance_history():
 out={};phase=Path('/workspace/scratch/1a661c5d6ceb/phase1-calibration/raw');found=Path('/workspace/scratch/1a661c5d6ceb/foundational-calibration/raw')
 for year in range(2010,2026):
  f=phase/f'pitching-{year}.json';f=f if f.exists() else found/f'mlb-pitching-{year}.json.gz'
  for b in old.read(f)['stats']:
   for z in b['splits']:out[z['player']['id'],year]={'GP':float(z['stat'].get('gamesPlayed',0)),'GS':float(z['stat'].get('gamesStarted',0))}
 return out

def observed_role(s,fallback):
 gp=s.get('GP',0);gs=s.get('GS',0)
 if gp>0:return 'SP' if gs/gp>=.5 else 'RP'
 return fallback # Missing appearances retain eligibility; short samples are flagged.

def role(p):
 position=p.get('position','');pit=p.get('pit',{});fallback='SP' if 'SP' in position else 'RP' if 'RP' in position or pit else 'H'
 if fallback=='H':return 'H'
 # Fantrax GP can include batting games for a two-way asset; it is not games pitched.
 if p.get('bat',{}).get('PA',0)>=100 and old.current(p,fallback).get('IP',0)>=20:return fallback
 if old.current(p,fallback).get('IP',0)==0:
  hist=[z for z in cf.seasons(p,fallback) if z['role']!='H' and z['stat'].get('IP',0)>0]
  if hist:
   latest=max(hist,key=lambda z:z['year']);return observed_role(appearance_history().get((latest['id'],latest['year']),{}),latest['role'])
 return observed_role(pit,fallback)

def seasons(p,rr):
 rows=copy.deepcopy(cf.seasons(p,rr));appear=appearance_history()
 for z in rows:
  if z['role']=='H':continue
  info=({'GS':p.get('pit',{}).get('GS',0),'GP':0} if p.get('bat',{}).get('PA',0)>=100 and z['stat'].get('IP',0)>=20 else p.get('pit',{})) if z['year']==2026 else appear.get((z['id'],z['year']),{})
  z['original_role']=z['role'];z['role']=observed_role(info,z['role'])
 return rows

# Two independent indexes: never compare PA to IP or discard a two-way stream.
HISTORY_H={(z['id'],z['year']):z for z in old.AN if z['role']=='H'}
HISTORY_P={(z['id'],z['year']):z for z in old.AN if z['role']!='H'}

def reconcile(s,policy=None):
 policy=policy or CONFIG['hitter_reconciliation'];z=s.copy();z['H']=min(z['H'],z['AB']);z['HR']=min(z['HR'],z['H']);parts=z['AB']+sum(z.get(k,0) for k in ['BB','HBP','SF'])
 if parts>z['PA']:
  if policy=='fixed_PA':
   fac=z['PA']/parts;z={k:v if k=='PA' else v*fac for k,v in z.items()}
  else:z['PA']=parts
 z['TB']=min(4*z['H'],max(z['H']+3*z['HR'],z['TB']));return z

@functools.lru_cache(None)
def curve(rr,age,q):
 # Rebuild only future lookups using separate streams; membership/anchors fixed.
 index=HISTORY_H if rr=='H' else HISTORY_P
 sample=[a for a in base.cohorts[rr] if abs(a['age']-age)<=2 and a['quality_bin']==q];band=2
 if len({a['id'] for a in sample})<20:sample=[a for a in base.cohorts[rr] if abs(a['age']-age)<=4 and a['quality_bin']==q];band=4
 if not sample:sample=base.cohorts[rr];band=None
 n=len({a['id'] for a in sample});shrink=n/(n+40);base_e=sum(r.exposure(a['anchor'],rr) for a in sample);rates0={k:sum(a['anchor'].get(k,0) for a in sample)/base_e for k in old.fields[rr]};out=[]
 for t in range(1,9):
  future=[base.annual(index.get((a['id'],a['year']+t))) for a in sample];future_e=sum(r.exposure(z,rr) for z in future);rates={}
  for k in old.fields[rr]:
   after=sum(z.get(k,0) for z in future)/future_e if future_e else 0;ratio=after/rates0[k] if rates0[k]>0 else 1;rates[k]=1 if k in ['PA','IP','AB'] else max(0,1+shrink*(ratio-1))
  out.append({'workload':max(0,future_e/base_e),'rates':rates})
 c={'anchors':len(sample),'unique_players':n,'age_band':band,'starting_contribution_quartile':q,'path':out,'warning':'Fixed cohort membership; separate H/P future indexes; historical attrition once'}
 if rr!='H' and CONFIG['leverage_policy']=='no_growth':
  for z in c['path']:
   for k in ['SV','HLD']:z['rates'][k]=min(1,z['rates'].get(k,1))
 return c

def recent_forecast(p,rr,scenario='base'):
 hist=seasons(p,rr);rows=[z for z in hist if 2023<=z['year']<=2026 and z['role']==rr and r.exposure(z['stat'],rr)>0]
 if not rows or not any(z['year']>=2024 for z in rows):return None
 weights={2023:.1,2024:.2,2025:.3,2026:.4};mass=sum(weights[z['year']] for z in rows);weighted=[(z['stat'],weights[z['year']]/mass) for z in rows];recent=sum(r.exposure(s,rr)*w for s,w in weighted);healthy=float(np.median(sorted([r.exposure(s,rr) for s,w in weighted],reverse=True)[:2]));prior=float(np.median([r.exposure(z['stat'],rr) for z in old.cal if z['role']==rr]));pw=1/(len(rows)+3);work=min(cf.cap(rr),(1-pw)*(.7*recent+.3*healthy)+pw*prior);strength=100 if rr=='H' else 30;rates={k:(sum(s.get(k,0)*w for s,w in weighted)+strength*old.prior[rr][k])/(recent+strength) for k in old.fields[rr]};exposure=sum(r.exposure(z['stat'],rr) for z in hist if z['role']==rr);reliability=exposure/(exposure+(600 if rr=='H' else 170));orig=base.recent_forecast(p,rr);audit=copy.deepcopy(orig[2]) if orig else copy.deepcopy(cf.forecast(p,rr)[2]) if cf.forecast(p,rr) else {};audit.update(estimator='V2.3 recent-performance with corrected observed-role routing',recent_observed_years=[z['year'] for z in rows],recent_workload=recent,healthy_observed_workload=healthy,projected_workload=work,role_workload_prior=prior,prior_weight=pw,rate_reliability=reliability,talent_rates=rates,role_changes=[{'year':z['year'],'from':z['original_role'],'to':z['role']} for z in hist if 'original_role' in z and z['original_role']!=z['role']]);audit['flags']=['Current rate evidence uses corrected primary observed role; short debut future role remains provisional','Original shared category scale, workload priors and aging-cohort membership retained; no market RP discount','Historical attrition applied once; no separate injury penalty'];return rates,work,audit

def mlb_role_paths(p,rr,scenario='base'):
 f=recent_forecast(p,rr,scenario)
 if not f:return None,None
 rates,work,audit=f;age=int(round(float(p.get('age') or 26)));q=int(np.searchsorted(base.CUTS[rr],r.surplus({k:v*work for k,v in rates.items()},rr)/work*r.REFERENCE[rr]));c=curve(rr,age,q);reliability=audit['rate_reliability'];spread=.25+.2*(1-reliability);factor_s=.85 if scenario=='low' else 1.15 if scenario=='high' else 1;out=[];means=[];states=[]
 for prob,factor in [(.25,1-spread),(.5,1),(.25,1+spread)]:
  path=[];statpath=[]
  for z in c['path']:
   s={k:v*z['rates'].get(k,1)*work*z['workload']*factor*factor_s for k,v in rates.items()}
   if rr=='H':s=reconcile(s)
   else:s['QA3']=min(s['QA3'],s['IP']/5)
   path.append(r.utility(r.surplus(s,rr)));statpath.append(s)
  out.append((prob,path));states.append(statpath)
  if factor==1:means=statpath
 return out,{'kind':'MLB','role':rr,'projection':means[0],'annual_projection':means,'outcome_state_projections':states,'projection_audit':audit,'MLB_evidence_reliability':reliability,'direct_aging_support':{k:v for k,v in c.items() if k!='path'},'flags':['V2.3 coherent hitter counts in every state/year; shared nonlinear utility applied once','Save/hold rate growth bounded by chronologically selected policy; innings attrition already retained','Category normalizers and replacement floors remain provisional, unchanged','Future role, playing time and availability are not individually predicted']}

def mlb_paths(p,scenario='base'):
 rr=role(p);paths,ma=mlb_role_paths(p,rr,scenario)
 if rr in ['SP','RP'] and old.current(p,'H').get('PA',0)>=100 and old.current(p,rr).get('IP',0)>=20:
  hs,ha=mlb_role_paths(p,'H',scenario)
  if paths and hs:
   gs=p.get('pit',{}).get('GS',0);ip=old.current(p,rr).get('IP',0);ipstart=ip/gs if gs>0 and ip>0 else 5.5;out=[];combined=[];stateprojections=[];overlaps=[]
   for j,(prob,hpath) in enumerate(hs):
    vals=[];statpath=[]
    for t,(h,s) in enumerate(zip(ha['outcome_state_projections'][j],ma['outcome_state_projections'][j])):
     overlap=min(1/6,max(0,ma['annual_projection'][t]['IP']/ipstart/162));h={k:v*(1-overlap) for k,v in h.items()};vals.append(r.utility(r.surplus(h,'H')+r.surplus(s,rr)));statpath.append({'hitting':h,'pitching':s})
     if j==1:overlaps.append(overlap)
    out.append((prob,vals));stateprojections.append(statpath)
    if j==1:combined=statpath
   audit=copy.deepcopy(ha);audit.update(role='H+SP',two_way_components={'H':{'audit':ha,'neutral_single_role':r.evaluate_paths(hs,'neutral')['display']},rr:{'audit':ma,'neutral_single_role':r.evaluate_paths(paths,'neutral')['display']}},two_way_policy='One asset; batting plus pitching, no DH on pitching days. Shared utility once after overlap removal.',two_way_annual_projection=combined,two_way_outcome_state_projections=stateprojections,two_way_overlap_fractions=overlaps);return out,audit
 return paths,ma

def player_paths(p,scenario='base'):
 mlb,ma=mlb_paths(p,scenario);pros,pa=r.prospect_paths(p,scenario) if p.get('prospect') else (None,None)
 if mlb and pros:
  w=ma['MLB_evidence_reliability'];return [(prob*w,v) for prob,v in mlb]+[(prob*(1-w),v) for prob,v in pros],{'kind':'hybrid','role':role(p),'MLB_reliability':w,'MLB':ma,'prospect':pa,'flags':['Frozen prospect distribution retained; corrected MLB evidence mixture; strengths remain provisional']}
 if mlb:return mlb,ma
 if pros:return pros,pa
 return [(1,[0.]*8)],{'kind':'unmodeled','role':role(p),'flags':['Unavailable estimate is not zero value']}

def evidence_warnings(p):
 flags=[];rr=role(p);ex=old.current(p,rr).get('PA' if rr=='H' else 'IP',0);profile=cf.PROFILES.get(p['id'],{});ident=profile.get('identifiers',{}).get('mlbamId');hist=profile.get('seasons',[]);years={z['year'] for z in hist if z['year']<2026};gaps=[y for y in range(min(years),max(years)+1) if y not in years] if years else []
 status={'current2026':'positive observed export exposure' if ex>0 else 'zero/missing export exposure: absence not independently verified','historical_no_MLB_record_years':gaps,'injury_diagnosis':'unavailable; no medical inference','mlbam_verified':bool(ident)}
 if ex==0 and hist:flags.append('Current availability uncertain: zero 2026 export exposure may represent absence or missing data. Value is conditional on the historical forecast; no extra injury haircut is applied.')
 if not ident and ex>0:flags.append('Identity warning: MLBAM unresolved. Only Fantrax-keyed recent counts support this estimate; full-career history is not independently verified.')
 if rr=='RP':flags.append('Relief deployment is optional: some teams forego SVH7 to protect ratios. An additional RP can have zero or negative marginal lineup impact. This contribution value is not a league trade-market price; no supported scarcity premium or arbitrary RP penalty is applied.')
 if p.get('prospect'):flags.append('Prospect ETA and saved level are provisional snapshots. Strategy-adjusted contribution measures production timing and risk, not retained resale value; a contender discount is not a trade-market price discount. Frozen rank/age probabilities do not directly model current MiLB skills or position scarcity.')
 pit=p.get('pit',{});gp=pit.get('GP',0);share=pit.get('GS',0)/gp if gp else None
 if 0<gp<10:flags.append('Small role sample: fewer than ten observed appearances; future starter/reliever role is provisional.')
 if share is not None and .25<share<.75:flags.append('Swingman role uncertainty: mixed starts/relief appearances. Primary observed role is used; future role may differ, and no supported probability mixture is available.')
 return status,flags

def build():
 D=copy.deepcopy(json.loads((ROOT/'trade-preview-v22/model/ui_catalog.json').read_text()));oldby={a['id']:a for a in D['assets']};rows=[];rolechanges=[]
 for a in D['assets']:
  if a['audit']['kind']=='pick':continue
  p=old.players[a['id']];paths,audit=player_paths(p);a['audit']=audit;a['values']={mode:r.evaluate_paths(paths,mode) for mode in r.MODES}
  if audit['kind']=='unmodeled':a['values']={mode:{'display':None,'underlying':None} for mode in r.MODES}
  a['annual_expected_utility']=[sum(prob*v[t] for prob,v in paths) for t in range(8)];a['range']={s:{mode:(r.evaluate_paths(player_paths(p,s)[0],mode)['display'] if audit['kind']!='unmodeled' else None) for mode in r.MODES} for s in ['low','high']};a.pop('career_memory_sensitivity',None);a['group']='MLB' if audit['kind'] in ['MLB','hybrid'] else 'Minors';status,flags=evidence_warnings(p);a['availability_status']=status;a['qualityWarnings']=flags;a['audit'].setdefault('flags',[]).extend(flags)
  prev=json.loads((ROOT/'trade-preview-v22/model/v22_results.json').read_text()) if False else None
  rows.append(a)
 for t in D['teams']:t['modeledPlayers']=sum(a['owner']==t['name'] and a['group'] in ['MLB','Minors'] and a['values']['neutral']['display'] is not None for a in D['assets'])
 by={a['id']:a for a in D['assets']}
 for t in D['trades']:
  for mode in r.MODES:
   packages=[sum(by[i]['values'][mode]['display'] for i in ids) for ids in t['identities']];bounds=[(sum(by[i]['range']['low'][mode] for i in ids),sum(by[i]['range']['high'][mode] for i in ids)) for ids in t['identities']];t['modes'][mode].update(package_values=packages,net_first_owner=packages[1]-packages[0],assumption_range=[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]])
 D.update(version='V2.3 correction candidate',warnings=D['warnings']+['V2.3 role routing and physical-count corrections; no production deployment','No model of actual trade-market acquisition cost; RP deployment is optional','Identity, current availability, swingman future roles and long-term category scale remain uncertain']);(P/'model/v23_results.json').write_text(json.dumps(D,indent=2));print('V2.3 candidate saved',len(D['assets']))
if __name__=='__main__':build()

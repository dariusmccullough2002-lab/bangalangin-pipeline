
## recovered/model/trade-preview-v23/model_v23.py
```python
   1: """Bounded V2.3 overlay. Never writes V2.2. Cached inputs and fixed common scale."""
   2: from pathlib import Path
   3: import sys,json,copy,functools,math
   4: import numpy as np
   5: sys.dont_write_bytecode=True
   6: P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path.insert(0,str(ROOT/'trade-preview-v22/model'));import model_v22 as base
   7: r=base.r;old=base.old;cf=base.cf
   8: CONFIG_PATH=P/'Selection.json'
   9: CONFIG=json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {'hitter_reconciliation':'fixed_PA','leverage_policy':'no_growth'}
  10: # GP/GS from cached official seasons; identity + season joins, never names.
  11: @functools.lru_cache(None)
  12: def appearance_history():
  13:  out={};phase=Path('/workspace/scratch/1a661c5d6ceb/phase1-calibration/raw');found=Path('/workspace/scratch/1a661c5d6ceb/foundational-calibration/raw')
  14:  for year in range(2010,2026):
  15:   f=phase/f'pitching-{year}.json';f=f if f.exists() else found/f'mlb-pitching-{year}.json.gz'
  16:   for b in old.read(f)['stats']:
  17:    for z in b['splits']:out[z['player']['id'],year]={'GP':float(z['stat'].get('gamesPlayed',0)),'GS':float(z['stat'].get('gamesStarted',0))}
  18:  return out
  19: 
  20: def observed_role(s,fallback):
  21:  gp=s.get('GP',0);gs=s.get('GS',0)
  22:  if gp>0:return 'SP' if gs/gp>=.5 else 'RP'
  23:  return fallback # Missing appearances retain eligibility; short samples are flagged.
  24: 
  25: def role(p):
  26:  position=p.get('position','');pit=p.get('pit',{});fallback='SP' if 'SP' in position else 'RP' if 'RP' in position or pit else 'H'
  27:  if fallback=='H':return 'H'
  28:  # Fantrax GP can include batting games for a two-way asset; it is not games pitched.
  29:  if p.get('bat',{}).get('PA',0)>=100 and old.current(p,fallback).get('IP',0)>=20:return fallback
  30:  if old.current(p,fallback).get('IP',0)==0:
  31:   hist=[z for z in cf.seasons(p,fallback) if z['role']!='H' and z['stat'].get('IP',0)>0]
  32:   if hist:
  33:    latest=max(hist,key=lambda z:z['year']);return observed_role(appearance_history().get((latest['id'],latest['year']),{}),latest['role'])
  34:  return observed_role(pit,fallback)
  35: 
  36: def seasons(p,rr):
  37:  rows=copy.deepcopy(cf.seasons(p,rr));appear=appearance_history()
  38:  for z in rows:
  39:   if z['role']=='H':continue
  40:   info=({'GS':p.get('pit',{}).get('GS',0),'GP':0} if p.get('bat',{}).get('PA',0)>=100 and z['stat'].get('IP',0)>=20 else p.get('pit',{})) if z['year']==2026 else appear.get((z['id'],z['year']),{})
  41:   z['original_role']=z['role'];z['role']=observed_role(info,z['role'])
  42:  return rows
  43: 
  44: # Two independent indexes: never compare PA to IP or discard a two-way stream.
  45: HISTORY_H={(z['id'],z['year']):z for z in old.AN if z['role']=='H'}
  46: HISTORY_P={(z['id'],z['year']):z for z in old.AN if z['role']!='H'}
  47: 
  48: def reconcile(s,policy=None):
  49:  policy=policy or CONFIG['hitter_reconciliation'];z=s.copy();z['H']=min(z['H'],z['AB']);z['HR']=min(z['HR'],z['H']);parts=z['AB']+sum(z.get(k,0) for k in ['BB','HBP','SF'])
  50:  if parts>z['PA']:
  51:   if policy=='fixed_PA':
  52:    fac=z['PA']/parts;z={k:v if k=='PA' else v*fac for k,v in z.items()}
  53:   else:z['PA']=parts
  54:  z['TB']=min(4*z['H'],max(z['H']+3*z['HR'],z['TB']));return z
  55: 
  56: @functools.lru_cache(None)
  57: def curve(rr,age,q):
  58:  # Rebuild only future lookups using separate streams; membership/anchors fixed.
  59:  index=HISTORY_H if rr=='H' else HISTORY_P
  60:  sample=[a for a in base.cohorts[rr] if abs(a['age']-age)<=2 and a['quality_bin']==q];band=2
  61:  if len({a['id'] for a in sample})<20:sample=[a for a in base.cohorts[rr] if abs(a['age']-age)<=4 and a['quality_bin']==q];band=4
  62:  if not sample:sample=base.cohorts[rr];band=None
  63:  n=len({a['id'] for a in sample});shrink=n/(n+40);base_e=sum(r.exposure(a['anchor'],rr) for a in sample);rates0={k:sum(a['anchor'].get(k,0) for a in sample)/base_e for k in old.fields[rr]};out=[]
  64:  for t in range(1,9):
  65:   future=[base.annual(index.get((a['id'],a['year']+t))) for a in sample];future_e=sum(r.exposure(z,rr) for z in future);rates={}
  66:   for k in old.fields[rr]:
  67:    after=sum(z.get(k,0) for z in future)/future_e if future_e else 0;ratio=after/rates0[k] if rates0[k]>0 else 1;rates[k]=1 if k in ['PA','IP','AB'] else max(0,1+shrink*(ratio-1))
  68:   out.append({'workload':max(0,future_e/base_e),'rates':rates})
  69:  c={'anchors':len(sample),'unique_players':n,'age_band':band,'starting_contribution_quartile':q,'path':out,'warning':'Fixed cohort membership; separate H/P future indexes; historical attrition once'}
  70:  if rr!='H' and CONFIG['leverage_policy']=='no_growth':
  71:   for z in c['path']:
  72:    for k in ['SV','HLD']:z['rates'][k]=min(1,z['rates'].get(k,1))
  73:  return c
  74: 
  75: def recent_forecast(p,rr,scenario='base'):
  76:  hist=seasons(p,rr);rows=[z for z in hist if 2023<=z['year']<=2026 and z['role']==rr and r.exposure(z['stat'],rr)>0]
  77:  if not rows or not any(z['year']>=2024 for z in rows):return None
  78:  weights={2023:.1,2024:.2,2025:.3,2026:.4};mass=sum(weights[z['year']] for z in rows);weighted=[(z['stat'],weights[z['year']]/mass) for z in rows];recent=sum(r.exposure(s,rr)*w for s,w in weighted);healthy=float(np.median(sorted([r.exposure(s,rr) for s,w in weighted],reverse=True)[:2]));prior=float(np.median([r.exposure(z['stat'],rr) for z in old.cal if z['role']==rr]));pw=1/(len(rows)+3);work=min(cf.cap(rr),(1-pw)*(.7*recent+.3*healthy)+pw*prior);strength=100 if rr=='H' else 30;rates={k:(sum(s.get(k,0)*w for s,w in weighted)+strength*old.prior[rr][k])/(recent+strength) for k in old.fields[rr]};exposure=sum(r.exposure(z['stat'],rr) for z in hist if z['role']==rr);reliability=exposure/(exposure+(600 if rr=='H' else 170));orig=base.recent_forecast(p,rr);audit=copy.deepcopy(orig[2]) if orig else copy.deepcopy(cf.forecast(p,rr)[2]) if cf.forecast(p,rr) else {};audit.update(estimator='V2.3 recent-performance with corrected observed-role routing',recent_observed_years=[z['year'] for z in rows],recent_workload=recent,healthy_observed_workload=healthy,projected_workload=work,role_workload_prior=prior,prior_weight=pw,rate_reliability=reliability,talent_rates=rates,role_changes=[{'year':z['year'],'from':z['original_role'],'to':z['role']} for z in hist if 'original_role' in z and z['original_role']!=z['role']]);audit['flags']=['Current rate evidence uses corrected primary observed role; short debut future role remains provisional','Original shared category scale, workload priors and aging-cohort membership retained; no market RP discount','Historical attrition applied once; no separate injury penalty'];return rates,work,audit
  79: 
  80: def mlb_role_paths(p,rr,scenario='base'):
  81:  f=recent_forecast(p,rr,scenario)
  82:  if not f:return None,None
  83:  rates,work,audit=f;age=int(round(float(p.get('age') or 26)));q=int(np.searchsorted(base.CUTS[rr],r.surplus({k:v*work for k,v in rates.items()},rr)/work*r.REFERENCE[rr]));c=curve(rr,age,q);reliability=audit['rate_reliability'];spread=.25+.2*(1-reliability);factor_s=.85 if scenario=='low' else 1.15 if scenario=='high' else 1;out=[];means=[];states=[]
  84:  for prob,factor in [(.25,1-spread),(.5,1),(.25,1+spread)]:
  85:   path=[];statpath=[]
  86:   for z in c['path']:
  87:    s={k:v*z['rates'].get(k,1)*work*z['workload']*factor*factor_s for k,v in rates.items()}
  88:    if rr=='H':s=reconcile(s)
  89:    else:s['QA3']=min(s['QA3'],s['IP']/5)
  90:    path.append(r.utility(r.surplus(s,rr)));statpath.append(s)
  91:   out.append((prob,path));states.append(statpath)
  92:   if factor==1:means=statpath
  93:  return out,{'kind':'MLB','role':rr,'projection':means[0],'annual_projection':means,'outcome_state_projections':states,'projection_audit':audit,'MLB_evidence_reliability':reliability,'direct_aging_support':{k:v for k,v in c.items() if k!='path'},'flags':['V2.3 coherent hitter counts in every state/year; shared nonlinear utility applied once','Save/hold rate growth bounded by chronologically selected policy; innings attrition already retained','Category normalizers and replacement floors remain provisional, unchanged','Future role, playing time and availability are not individually predicted']}
  94: 
  95: def mlb_paths(p,scenario='base'):
  96:  rr=role(p);paths,ma=mlb_role_paths(p,rr,scenario)
  97:  if rr in ['SP','RP'] and old.current(p,'H').get('PA',0)>=100 and old.current(p,rr).get('IP',0)>=20:
  98:   hs,ha=mlb_role_paths(p,'H',scenario)
  99:   if paths and hs:
 100:    gs=p.get('pit',{}).get('GS',0);ip=old.current(p,rr).get('IP',0);ipstart=ip/gs if gs>0 and ip>0 else 5.5;out=[];combined=[];stateprojections=[];overlaps=[]
 101:    for j,(prob,hpath) in enumerate(hs):
 102:     vals=[];statpath=[]
 103:     for t,(h,s) in enumerate(zip(ha['outcome_state_projections'][j],ma['outcome_state_projections'][j])):
 104:      overlap=min(1/6,max(0,ma['annual_projection'][t]['IP']/ipstart/162));h={k:v*(1-overlap) for k,v in h.items()};vals.append(r.utility(r.surplus(h,'H')+r.surplus(s,rr)));statpath.append({'hitting':h,'pitching':s})
 105:      if j==1:overlaps.append(overlap)
 106:     out.append((prob,vals));stateprojections.append(statpath)
 107:     if j==1:combined=statpath
 108:    audit=copy.deepcopy(ha);audit.update(role='H+SP',two_way_components={'H':{'audit':ha,'neutral_single_role':r.evaluate_paths(hs,'neutral')['display']},rr:{'audit':ma,'neutral_single_role':r.evaluate_paths(paths,'neutral')['display']}},two_way_policy='One asset; batting plus pitching, no DH on pitching days. Shared utility once after overlap removal.',two_way_annual_projection=combined,two_way_outcome_state_projections=stateprojections,two_way_overlap_fractions=overlaps);return out,audit
 109:  return paths,ma
 110: 
 111: def player_paths(p,scenario='base'):
 112:  mlb,ma=mlb_paths(p,scenario);pros,pa=r.prospect_paths(p,scenario) if p.get('prospect') else (None,None)
 113:  if mlb and pros:
 114:   w=ma['MLB_evidence_reliability'];return [(prob*w,v) for prob,v in mlb]+[(prob*(1-w),v) for prob,v in pros],{'kind':'hybrid','role':role(p),'MLB_reliability':w,'MLB':ma,'prospect':pa,'flags':['Frozen prospect distribution retained; corrected MLB evidence mixture; strengths remain provisional']}
 115:  if mlb:return mlb,ma
 116:  if pros:return pros,pa
 117:  return [(1,[0.]*8)],{'kind':'unmodeled','role':role(p),'flags':['Unavailable estimate is not zero value']}
 118: 
 119: def evidence_warnings(p):
 120:  flags=[];rr=role(p);ex=old.current(p,rr).get('PA' if rr=='H' else 'IP',0);profile=cf.PROFILES.get(p['id'],{});ident=profile.get('identifiers',{}).get('mlbamId');hist=profile.get('seasons',[]);years={z['year'] for z in hist if z['year']<2026};gaps=[y for y in range(min(years),max(years)+1) if y not in years] if years else []
 121:  status={'current2026':'positive observed export exposure' if ex>0 else 'zero/missing export exposure: absence not independently verified','historical_no_MLB_record_years':gaps,'injury_diagnosis':'unavailable; no medical inference','mlbam_verified':bool(ident)}
 122:  if ex==0 and hist:flags.append('Current availability uncertain: zero 2026 export exposure may represent absence or missing data. Value is conditional on the historical forecast; no extra injury haircut is applied.')
 123:  if not ident and ex>0:flags.append('Identity warning: MLBAM unresolved. Only Fantrax-keyed recent counts support this estimate; full-career history is not independently verified.')
 124:  if rr=='RP':flags.append('Relief deployment is optional: some teams forego SVH7 to protect ratios. An additional RP can have zero or negative marginal lineup impact. This contribution value is not a league trade-market price; no supported scarcity premium or arbitrary RP penalty is applied.')
 125:  if p.get('prospect'):flags.append('Prospect ETA and saved level are provisional snapshots. Strategy-adjusted contribution measures production timing and risk, not retained resale value; a contender discount is not a trade-market price discount. Frozen rank/age probabilities do not directly model current MiLB skills or position scarcity.')
 126:  pit=p.get('pit',{});gp=pit.get('GP',0);share=pit.get('GS',0)/gp if gp else None
 127:  if 0<gp<10:flags.append('Small role sample: fewer than ten observed appearances; future starter/reliever role is provisional.')
 128:  if share is not None and .25<share<.75:flags.append('Swingman role uncertainty: mixed starts/relief appearances. Primary observed role is used; future role may differ, and no supported probability mixture is available.')
 129:  return status,flags
 130: 
 131: def build():
 132:  D=copy.deepcopy(json.loads((ROOT/'trade-preview-v22/model/ui_catalog.json').read_text()));oldby={a['id']:a for a in D['assets']};rows=[];rolechanges=[]
 133:  for a in D['assets']:
 134:   if a['audit']['kind']=='pick':continue
 135:   p=old.players[a['id']];paths,audit=player_paths(p);a['audit']=audit;a['values']={mode:r.evaluate_paths(paths,mode) for mode in r.MODES}
 136:   if audit['kind']=='unmodeled':a['values']={mode:{'display':None,'underlying':None} for mode in r.MODES}
 137:   a['annual_expected_utility']=[sum(prob*v[t] for prob,v in paths) for t in range(8)];a['range']={s:{mode:(r.evaluate_paths(player_paths(p,s)[0],mode)['display'] if audit['kind']!='unmodeled' else None) for mode in r.MODES} for s in ['low','high']};a.pop('career_memory_sensitivity',None);a['group']='MLB' if audit['kind'] in ['MLB','hybrid'] else 'Minors';status,flags=evidence_warnings(p);a['availability_status']=status;a['qualityWarnings']=flags;a['audit'].setdefault('flags',[]).extend(flags)
 138:   prev=json.loads((ROOT/'trade-preview-v22/model/v22_results.json').read_text()) if False else None
 139:   rows.append(a)
 140:  for t in D['teams']:t['modeledPlayers']=sum(a['owner']==t['name'] and a['group'] in ['MLB','Minors'] and a['values']['neutral']['display'] is not None for a in D['assets'])
 141:  by={a['id']:a for a in D['assets']}
 142:  for t in D['trades']:
 143:   for mode in r.MODES:
 144:    packages=[sum(by[i]['values'][mode]['display'] for i in ids) for ids in t['identities']];bounds=[(sum(by[i]['range']['low'][mode] for i in ids),sum(by[i]['range']['high'][mode] for i in ids)) for ids in t['identities']];t['modes'][mode].update(package_values=packages,net_first_owner=packages[1]-packages[0],assumption_range=[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]])
 145:  D.update(version='V2.3 correction candidate',warnings=D['warnings']+['V2.3 role routing and physical-count corrections; no production deployment','No model of actual trade-market acquisition cost; RP deployment is optional','Identity, current availability, swingman future roles and long-term category scale remain uncertain']);(P/'model/v23_results.json').write_text(json.dumps(D,indent=2));print('V2.3 candidate saved',len(D['assets']))
 146: if __name__=='__main__':build()
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/opportunity_models.py
```python
   1: """Past-only expected MLB workload models; no player overrides or production writes."""
   2: import os
   3: os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
   4: import sys,json,copy,csv,math,hashlib,gzip,collections,functools,ast
   5: from pathlib import Path
   6: import numpy as np
   7: from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
   8: from sklearn.pipeline import make_pipeline
   9: from sklearn.preprocessing import StandardScaler
  10: from sklearn.linear_model import Ridge
  11: from threadpoolctl import threadpool_limits
  12: threadpool_limits(1)
  13: sys.dont_write_bytecode=True
  14: OUT=Path(__file__).resolve().parent;PARENT=OUT.parent
  15: sys.path.insert(0,str(PARENT))
  16: # Reuse saved helpers only; do not execute completed collection or scoring loops.
  17: helper=PARENT/'validate_debut.py';source=helper.read_text().split("methods=['baseline'")[0];env={'__file__':str(helper),'__name__':'debut_helpers'}
  18: exec(compile(source,str(helper),'exec'),env)
  19: m,v,r,old=(env[k] for k in ['m','v','r','old']);hist,lookup,first,index=(env[k] for k in ['hist','lookup','first','index']);forecast,project=env['forecast'],env['project'];catalog=env['catalog'];appear=env['appear']
  20: minor={(ident,year):sum(z['outs'] for z in zs)/3 for (ident,year),zs in index.items()};complete=env['complete']
  21: NAMES=['latest','lag1','lag2','lag3','calendar_mean','positive_mean','highest','lowest','stdev','positive_years','zero_years','durable_run','recent_change','age','years_since_debut','current_GP','current_GS','current_GS_fraction','previous_GS_fraction','debut_MLB_workload','debut_MiLB_workload','debut_professional_capacity','debut_MLB_share','capacity_missing','current_MiLB_workload','current_professional_capacity','role_changed','career_positive_seasons','age_x_latest']
  22: METHODS=['ridge','direct_tree','hurdle','hurdle_no_capacity','hurdle_bounded2020']
  23: CAPACITY_COLUMNS=[19,20,21,22,23,24,25]
  24: SETTINGS={'max_iter':100,'max_leaf_nodes':15,'min_samples_leaf':30,'learning_rate':.07,'l2_regularization':10,'random_state':2309}
  25: def age(ident,year):
  26:  a=r.age_at(ident,year)
  27:  return float(a) if a is not None and math.isfinite(a) else None
  28: def features(rows,rr,year,ident,bounded=False):
  29:  stream='H' if rr=='H' else 'P';past=[z for z in rows if z['year']<=year and r.exposure(z['stat'],rr)>0]
  30:  if not past:return None
  31:  by={z['year']:z for z in past};debut=min(z['year'] for z in past);a=age(ident,year)
  32:  if a is None:return None
  33:  def exposure(y):
  34:   z=by.get(y);e=r.exposure(z['stat'],rr) if z else 0
  35:   if bounded and y==2020:
  36:    prior=[r.exposure(t['stat'],rr) for t in past if t['year']<2020]
  37:    if prior:e=min(e*162/60,max(prior))
  38:   return e
  39:  work=[exposure(y) for y in range(year,year-4,-1)];pos=[x for x in work if x>0];run=0;threshold=600 if rr=='H' else 150 if rr=='SP' else 50
  40:  for y in range(year,year-6,-1):
  41:   z=by.get(y);e=r.exposure(z['stat'],rr) if z else 0
  42:   # Schedule-aware durability classification, not synthesized talent or target counts.
  43:   if e>=(threshold*60/162 if y==2020 else threshold):run+=1
  44:   else:break
  45:  current=by.get(year);previous=by.get(year-1);curinfo=appear.get((ident,year),{}) if rr!='H' else {};previnfo=appear.get((ident,year-1),{}) if rr!='H' else {}
  46:  if current and year==2026 and rr!='H':curinfo=current.get('stat',{})
  47:  gp=curinfo.get('GP',curinfo.get('gamesPlayed',0));gs=curinfo.get('GS',curinfo.get('gamesStarted',0));pg=previnfo.get('GP',0);ps=previnfo.get('GS',0)
  48:  actualdebut=first.get(ident) if rr!='H' else debut;drow=by.get(actualdebut);di=r.exposure(drow['stat'],rr) if drow else 0
  49:  verified=bool(rr!='H' and actualdebut and actualdebut<=year and complete.get(actualdebut,set())==set(range(11,17)))
  50:  mi=minor.get((ident,actualdebut),0) if verified else 0;pro=di+mi;currentmi=minor.get((ident,year),0) if rr!='H' and complete.get(year,set())==set(range(11,17)) else 0
  51:  x=[*work,float(np.mean(work)),float(np.mean(pos)) if pos else 0,max(pos) if pos else 0,min(pos) if pos else 0,float(np.std(work)),len(pos),sum(y>=debut and exposure(y)==0 for y in range(year-3,year+1)),run,work[0]-work[1],a,min(30,year-debut),gp,gs,gs/gp if gp else 0,ps/pg if pg else 0,di,mi,pro,di/pro if pro else 0,0 if verified or rr=='H' else 1,currentmi,work[0]+currentmi,int(bool(current and previous and current['role']!=previous['role'])),len(past),a*work[0]/100]
  52:  assert len(x)==len(NAMES)
  53:  return np.asarray(x,dtype=float)
  54: def groups_for(rows,rr,year,ident):
  55:  f=features(rows,rr,year,ident);a=f[13];g=['all',rr,'young' if a<=26 else 'established',f'anchor_{year}']
  56:  if rr=='H':
  57:   if f[11]>=4:g.append('durable_four_years')
  58:   elif f[0]>=400:g.append('ordinary_regular')
  59:   else:g.append('part_time_or_returning')
  60:   if a>=33:g.append('aging_33plus')
  61:   short=0
  62:   for z in rows:
  63:    if year-3<=z['year']<=year:
  64:     threshold=400*60/162 if z['year']==2020 else 400
  65:     short+=z['stat'].get('PA',0)<threshold
  66:   if short>=2:g.append('repeated_shortfall_proxy_not_diagnosed_injury')
  67:  else:
  68:   debut=first.get(ident)
  69:   if debut==year:g.append('first_MLB_season')
  70:   if debut==year-1:g.append('second_MLB_season')
  71:   if f[17]>0 and f[17]<1:g.append('swingmen')
  72:   if f[20]>0 and debut and debut>=year-3:g.append('recent_debut_with_MiLB')
  73:  return g
  74: records={rr:[] for rr in ['H','SP','RP']}
  75: for (ident,stream),rows in hist.items():
  76:  earliest=min(z['year'] for z in rows)
  77:  for year in range(max(2013,earliest),2025):
  78:   recent=[z for z in rows if z['year']<=year and z['year']>=year-2 and r.exposure(z['stat'],'H' if stream=='H' else 'SP')>0]
  79:   if not recent:continue
  80:   latest=max(recent,key=lambda z:z['year']);rr=latest['role'];current=lookup.get((ident,year,stream))
  81:   if stream=='H' and max(z['stat'].get('PA',0) for z in recent)<100:continue
  82:   a=age(ident,year)
  83:   if a is None:continue
  84:   f=features(rows,rr,year,ident);fb=features(rows,rr,year,ident,True)
  85:   target=lookup.get((ident,year+1,stream));actual=target['stat'] if target else {};y=r.exposure(actual,rr)
  86:   records[rr].append({'id':ident,'year':year,'name':latest['name'],'role':rr,'x':f,'bounded_x':fb,'target':y,'actual':actual,'groups':groups_for(rows,rr,year,ident),'positive_anchor':bool(current and r.exposure(current['stat'],rr)>0)})
  87: print('Records',{rr:len(xs) for rr,xs in records.items()},flush=True)
  88: def fit(rows,method):
  89:  X=np.stack([z['bounded_x'] if method=='hurdle_bounded2020' else z['x'] for z in rows]);y=np.asarray([z['target'] for z in rows])
  90:  if method=='hurdle_no_capacity':X[:,CAPACITY_COLUMNS]=0
  91:  if method=='ridge':model=make_pipeline(StandardScaler(),Ridge(alpha=100));model.fit(X,y);return model,None
  92:  if method=='direct_tree':model=HistGradientBoostingRegressor(loss='squared_error',**SETTINGS);model.fit(X,y);return model,None
  93:  active=y>0;participation=HistGradientBoostingClassifier(**SETTINGS);participation.fit(X,active)
  94:  model=HistGradientBoostingRegressor(loss='squared_error',**SETTINGS);model.fit(X[active],y[active]);return model,participation
  95: def predict(models,rows,method,cap):
  96:  X=np.stack([z['bounded_x'] if method=='hurdle_bounded2020' else z['x'] for z in rows])
  97:  if method=='hurdle_no_capacity':X[:,CAPACITY_COLUMNS]=0
  98:  model,part=models;conditional=np.maximum(0,model.predict(X));prob=part.predict_proba(X)[:,1] if part is not None else np.ones(len(rows));means=np.minimum(cap,conditional*prob)
  99:  return means,prob,conditional
 100: def training(rr,anchor,development=False,raw_covid=False):
 101:  return [z for z in records[rr] if z['year']+1<=anchor and z['id']%5 not in ([0,4] if development else [0]) and (raw_covid or z['year'] not in [2019,2020])]
 102: @functools.lru_cache(None)
 103: def cap_at(rr,anchor):
 104:  vals=[r.exposure(z['stat'],rr) for z in old.AN if z['role']==rr and z['year']<=anchor and z['year']!=2020 and r.exposure(z['stat'],rr)>0]
 105:  return float(np.quantile(vals,.995))
 106: ANCHORS=[2016,2017,2018,2021,2022,2023,2024]
 107: saved_pitch=json.loads((PARENT/'Debut_Chronological_Cases.json').read_text());preserved={(z['mlbam_id'],z['anchor']):z for z in saved_pitch}
 108: devscores={};test=[];selected={};training_manifest=[]
 109: for rr in ['H','SP','RP']:
 110:  development={method:[] for method in METHODS}
 111:  for year in [2016,2017,2018,2021,2022]:
 112:   train=training(rr,year,True);dev=[z for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
 113:   if not dev:continue
 114:   for method in METHODS:
 115:    model=fit(train,method);pred,prob,cond=predict(model,dev,method,cap_at(rr,year));development[method].extend([(float(a),z['target']) for a,z in zip(pred,dev)])
 116:  devscores[rr]={method:{'n':len(xs),'MAE':float(np.mean([abs(a-b) for a,b in xs])),'bias':float(np.mean([a-b for a,b in xs]))} for method,xs in development.items()}
 117:  # Fixed selection objective chosen before scoring: MAE plus one-quarter absolute signed bias.
 118:  selected[rr]=min(METHODS,key=lambda method:devscores[rr][method]['MAE']+.25*abs(devscores[rr][method]['bias']))
 119:  print('Selected from development',rr,selected[rr],devscores[rr],flush=True)
 120:  for year in ANCHORS:
 121:   train=training(rr,year);xs=[z for z in records[rr] if z['year']==year and z['id']%5==0 and z['positive_anchor'] and (rr=='H' or (z['id'],year) in preserved)]
 122:   if not xs:continue
 123:   predictions={};modelmeta={}
 124:   for method in METHODS:
 125:    model=fit(train,method);pred,prob,cond=predict(model,xs,method,cap_at(rr,year));predictions[method]=pred;modelmeta[method]=(prob,cond)
 126:   training_manifest.append({'role':rr,'forecast_anchor':year,'train_rows':len(train),'train_id_mods':sorted({z['id']%5 for z in train}),'latest_training_target':max(z['year']+1 for z in train),'test_n':len(xs),'cap':cap_at(rr,year)})
 127:   for j,z in enumerate(xs):
 128:    rows=hist[z['id'],'H' if rr=='H' else 'P'];base=forecast(rows,rr,year,z['id'],strict=True)
 129:    if not base:continue
 130:    baseline=preserved[z['id'],year]['baseline'] if rr!='H' else project(base,rr,z['x'][13],year,True)
 131:    exposure=baseline.get('PA' if rr=='H' else 'IP',0);result={'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':rr,'groups':z['groups'],'actual':z['actual'],'baseline':baseline,'chosen_method':selected[rr]}
 132:    for method in METHODS:
 133:     expected=float(predictions[method][j]);ratio=expected/exposure if exposure else 0;stat={k:value*ratio for k,value in baseline.items()}
 134:     if rr!='H':
 135:      for k in ['SV','HLD']:stat[k]=baseline.get(k,0)*min(1,ratio) # separate opportunity forecast, no workload-created leverage
 136:      stat['QA3']=min(stat.get('QA3',0),stat['IP']/5)
 137:     else:stat=v.reconcile(stat)
 138:     result[method]=stat
 139:    result['selected']=result[selected[rr]];test.append(result)
 140:  print('Completed test role',rr,flush=True)
 141: def scores(cases):
 142:  out={}
 143:  for group in sorted({g for z in cases for g in z['groups']}):
 144:   xs=[z for z in cases if group in z['groups']];metrics={}
 145:   for k in ['PA','IP','K','ER','BB','H','QA3','HR','R','RBI','SB','SV','HLD']:
 146:    valid=[z for z in xs if k in z['baseline'] and (k in z['actual'] or not z['actual'])]
 147:    if not valid:continue
 148:    metrics[k]={}
 149:    for method in ['baseline',*METHODS,'selected']:
 150:     errors=np.asarray([z[method].get(k,0)-z['actual'].get(k,0) for z in valid]);metrics[k][method]={'n':len(valid),'MAE':float(np.mean(np.abs(errors))),'bias':float(np.mean(errors)),'RMSE':float(np.sqrt(np.mean(errors**2)))}
 151:   out[group]={'n':len(xs),'metrics':metrics}
 152:  return out
 153: result={'methods':METHODS,'selected_by_development':selected,'development_scores':devscores,'test_scores':scores(test),'pitcher_test_case_count':sum(z['role']!='H' for z in test),'hitter_test_case_count':sum(z['role']=='H' for z in test),'training_manifest':training_manifest,'features':NAMES,'settings':SETTINGS,'selection_rule':'Development MAE +.25absolute bias; no test-label selection','covid_training_policy':'Exclude2019 anchors(target2020) and2020 anchors; bounded variant changes2020 workload features only','saved_baseline_reused':True}
 154: assert result['pitcher_test_case_count']==1084
 155: (OUT/'Opportunity_Validation.json').write_text(json.dumps(result,indent=2));(OUT/'Opportunity_Test_Cases.json.gz').write_bytes(gzip.compress(json.dumps(test,separators=(',',':')).encode(),mtime=0))
 156: print('Historical testing saved',flush=True)
 157: # Exact original94 benchmark subset, reuse baseline as originally frozen; scale category rates from saved baseline.
 158: frozen94=json.loads((PARENT/'Historical_Cases.json').read_text());testby={(z['mlbam_id'],z['anchor']):z for z in test if z['role']!='H'};frozen=[]
 159: for z in frozen94:
 160:  t=testby[z['mlbam_id'],z['anchor']];o=t|{'baseline':z['baseline'],'groups':z['subgroups']}
 161:  for method in [*METHODS,'selected']:
 162:   expected=t[method]['IP'];ratio=expected/z['baseline']['IP'];o[method]={k:value*ratio for k,value in z['baseline'].items()}
 163:   for k in ['SV','HLD']:o[method][k]=z['baseline'].get(k,0)*min(1,ratio)
 164:  frozen.append(o)
 165: (OUT/'Opportunity_Frozen94.json').write_text(json.dumps(scores(frozen),indent=2))
 166: # Current impact, first-year only; prospects, picks, uncertain identities keep original paths.
 167: currentalternatives={rr:{method:fit(training(rr,2026),method) for method in METHODS} for rr in ['H','SP','RP']}
 168: currentmodels={rr:currentalternatives[rr][selected[rr]] for rr in ['H','SP','RP']};current=[];unchanged=[];maxbaseline=0
 169: def component(audit,rr):
 170:  audit=audit.get('MLB',audit);z=audit.get('two_way_components',{}).get(rr,audit);return z.get('audit',z)
 171: for asset in catalog['assets']:
 172:  p=old.players.get(asset['id']);ident=v.cf.IDS.get(asset['id'],p.get('mlbamId') if p else None)
 173:  if not p or not ident or not asset.get('audit',{}).get('MLB',asset.get('audit',{})).get('projection'):
 174:   unchanged.append({'id':asset['id'],'reason':'Pick/prospect/unresolved or no modeled MLB projection'});continue
 175:  roles=['H',v.role(p)] if asset['audit'].get('role')=='H+SP' else [v.role(p)];changedstreams=[];originalpaths,audit=m.paths(p);newpaths=[(prob,list(path)) for prob,path in originalpaths]
 176:  for rr in roles:
 177:   if rr not in currentmodels:continue
 178:   rows=v.seasons(p,rr);f=v.recent_forecast(p,rr)
 179:   if not f:continue
 180:   x=features(rows,rr,2026,ident);xb=features(rows,rr,2026,ident,True)
 181:   if x is None:continue
 182:   d={'x':x,'bounded_x':xb};method=selected[rr];pred,prob,cond=predict(currentmodels[rr],[d],method,cap_at(rr,2026));baseau=component(asset['audit'],rr);baseprojection=baseau['projection'];exposure=baseprojection.get('PA' if rr=='H' else 'IP',0);expected=float(pred[0]);factor=expected/exposure if exposure else 0
 183:   baseline_states=v.mlb_role_paths(p,rr)[1]['outcome_state_projections'];newstates=[]
 184:   for states in baseline_states:
 185:    st={k:value*factor for k,value in states[0].items()}
 186:    if rr!='H':
 187:     for k in ['SV','HLD']:st[k]=states[0].get(k,0)*min(1,factor)
 188:     st['QA3']=min(st['QA3'],st['IP']/5)
 189:    else:st=v.reconcile(st)
 190:    newstates.append(st)
 191:   utilities=[r.utility(r.surplus(st,rr)) for st in newstates]
 192:   if len(roles)==1:
 193:    # MLB atoms precede retained prospect atoms in the preserved mixture.
 194:    # Change only the three MLB states; keep prospect paths and mixture weights intact.
 195:    assert len(newpaths)>=3
 196:    for j in range(3):newpaths[j][1][0]=utilities[j]
 197:   candidate={k:value*factor for k,value in baseprojection.items()}
 198:   if rr!='H':
 199:    for k in ['SV','HLD']:candidate[k]=baseprojection.get(k,0)*min(1,factor)
 200:    candidate['QA3']=min(candidate['QA3'],candidate['IP']/5)
 201:   else:candidate=v.reconcile(candidate)
 202:   changedstreams.append({'role':rr,'method':method,'baseline':baseprojection,'candidate':candidate,'expected_MLB_workload':expected,'participation_probability':float(prob[0]),'conditional_workload':float(cond[0]),'features':dict(zip(NAMES,map(float,x))),'MLB_talent_rates_unchanged':True,'rate_aging_unchanged':True,'later_years_unchanged':True})
 203:  if len(roles)>1:
 204:   unchanged.append({'id':asset['id'],'reason':'Two-way streams audited; combined valuation kept frozen pending overlap/distribution validation','experimental_streams':changedstreams});continue
 205:  if not changedstreams:
 206:   unchanged.append({'id':asset['id'],'reason':'No supported MLB workload features'});continue
 207:  for (oldprob,oldpath),(newprob,newpath) in zip(originalpaths,newpaths):
 208:   assert oldprob==newprob and oldpath[1:]==newpath[1:]
 209:  assert originalpaths[3:]==newpaths[3:]
 210:  baselinefit={mode:m.competitive(originalpaths,mode) for mode in r.MODES};candidatefit={mode:m.competitive(newpaths,mode) for mode in r.MODES};maxbaseline=max(maxbaseline,abs(baselinefit['neutral']['display']-asset['values']['neutral']['display']))
 211:  alternatives={}
 212:  for variant in METHODS:
 213:   vp,vprob,vcond=predict(currentalternatives[rr][variant],[d],variant,cap_at(rr,2026));vratio=float(vp[0])/exposure;vstates=[]
 214:   for states in baseline_states:
 215:    st={k:value*vratio for k,value in states[0].items()}
 216:    if rr!='H':
 217:     for k in ['SV','HLD']:st[k]=states[0].get(k,0)*min(1,vratio)
 218:    else:st=v.reconcile(st)
 219:    vstates.append(st)
 220:   vpaths=[(pr,list(path)) for pr,path in originalpaths]
 221:   for j in range(3):vpaths[j][1][0]=r.utility(r.surplus(vstates[j],rr))
 222:   vs={k:value*vratio for k,value in baseprojection.items()}
 223:   if rr!='H':
 224:    for k in ['SV','HLD']:vs[k]=baseprojection.get(k,0)*min(1,vratio)
 225:   else:vs=v.reconcile(vs)
 226:   alternatives[variant]={'projection':vs,'neutral':m.competitive(vpaths,'neutral')['display'],'competitive_fit':{mode:m.competitive(vpaths,mode)['display'] for mode in r.MODES},'participation_probability':float(vprob[0]),'conditional_workload':float(vcond[0])}
 227:  assert abs(alternatives[selected[rr]]['neutral']-candidatefit['neutral']['display'])<1e-8
 228:  current.append({'id':asset['id'],'name':asset['name'],'owner':asset['owner'],'age':p.get('age'),'streams':changedstreams,'baseline_neutral':asset['values']['neutral']['display'],'candidate_neutral':candidatefit['neutral']['display'],'baseline_competitive_fit':{k:z['display'] for k,z in baselinefit.items()},'candidate_competitive_fit':{k:z['display'] for k,z in candidatefit.items()},'value_delta':candidatefit['neutral']['display']-asset['values']['neutral']['display'],'alternatives':alternatives})
 229:  print('',end='',flush=True)
 230: (OUT/'Opportunity_Current_Impact.json.gz').write_bytes(gzip.compress(json.dumps(current,indent=2).encode(),mtime=0));(OUT/'Unaffected_Assets.json.gz').write_bytes(gzip.compress(json.dumps(unchanged,indent=2).encode(),mtime=0))
 231: csvrows=[]
 232: for z in current:
 233:  st=z['streams'][0];key='PA' if st['role']=='H' else 'IP';delta=st['candidate'][key]-st['baseline'][key]
 234:  if abs(delta)<(10 if key=='PA' else 1) and abs(z['value_delta'])<1:continue
 235:  row={'id':z['id'],'player':z['name'],'fantasy_organization':'Island' if z['owner'].casefold()=='epskenes island' else z['owner'],'age':z['age'],'role':st['role'],'method':st['method'],'participation_probability':st['participation_probability'],'conditional_workload':st['conditional_workload'],'baseline_neutral':z['baseline_neutral'],'candidate_neutral':z['candidate_neutral'],'value_delta':z['value_delta']}
 236:  for k in ['PA','IP','K','ER','BB','H','QA3','HR','R','RBI','SB','SV','HLD']:row['baseline_'+k]=st['baseline'].get(k);row['candidate_'+k]=st['candidate'].get(k)
 237:  for mode in r.MODES:row['baseline_fit_'+mode]=z['baseline_competitive_fit'][mode];row['candidate_fit_'+mode]=z['candidate_competitive_fit'][mode]
 238:  csvrows.append(row)
 239: with (OUT/'Opportunity_Material_Impact.csv').open('w') as file:
 240:  w=csv.DictWriter(file,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
 241: reg={'asset_count':len(catalog['assets']),'current_modeled_changed':len(current),'untouched':len(unchanged),'original_catalog_sha256':hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),'max_baseline_value_reproduction_error':maxbaseline,'production_changes':False,'all_IDs_owners_picks_unchanged':True,'experimental_first_year_only':True,'MLB_talent_and_rate_aging_unchanged':True,'save_hold_totals_never_increased':True,'two_way_valuation_held_frozen':True,'later_years_and_prospect_paths_unchanged':True,'uncertainty_distribution':'Frozen mean-one states rescaled; not recalibrated, no probabilistic superiority claim'}
 242: assert len(current)+len(unchanged)==2546;assert maxbaseline<1e-7
 243: (OUT/'Opportunity_Regression.json').write_text(json.dumps(reg,indent=2));print('DONE',reg,flush=True)
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/shared.py
```python
   1: """Read-only shared helpers for the existing audit; no collection or prior fit loops."""
   2: import sys,json,gzip,functools,copy,math
   3: from pathlib import Path
   4: import numpy as np
   5: from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
   6: from sklearn.pipeline import make_pipeline
   7: from sklearn.preprocessing import StandardScaler
   8: from sklearn.linear_model import Ridge,LogisticRegression
   9: OUT=Path(__file__).resolve().parent;PARENT=OUT.parent
  10: main=PARENT/'quality_aware.py';e={'__file__':str(main),'__name__':'joint_helpers'}
  11: exec(compile(main.read_text().split('cases=[];manifest=[]')[0],str(main),'exec'),e)
  12: base=e['env'];records=e['records'];lookup=e['lookup'];appear=base['appear'];index=e['index'];first=e['first'];settings=e['settings'];hist=base['hist'];r=base['r'];v=base['v'];m=base['m'];old=base['old'];catalog=base['catalog'];games=r.G
  13: def save(name,value):
  14:  s=json.dumps(value,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x)
  15:  if name.endswith('.gz'):(OUT/name).write_bytes(gzip.compress(s.encode(),mtime=0))
  16:  else:(OUT/name).write_text(s)
  17: def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
  18: def metric(pairs):
  19:  a=np.array([x-y for x,y in pairs]);return {'n':len(a),'MAE':float(np.mean(abs(a))),'bias':float(np.mean(a)),'RMSE':float(np.sqrt(np.mean(a*a)))} if len(a) else {'n':0,'MAE':None,'bias':None,'RMSE':None}
  20: def target(z,h=1):return lookup.get((z['id'],z['year']+h,'H' if z['role']=='H' else 'P'))
  21: def counts(ident,year):
  22:  a=appear.get((ident,year));b=games['annual_QA3'].get(str(year),{}).get(str(ident))
  23:  if a is None:return None
  24:  gp=a.get('GP',0);gs=a.get('GS',0)
  25:  return {'GP':gp,'GS':gs,'RA':max(0,gp-gs),'QA3':b.get('QA3') if b else None,'exact_QA3_available':bool(b)}
  26: def capacity(ident,year):
  27:  rows=hist.get((ident,'P'),[]);vals=[]
  28:  for a in rows:
  29:   if a['year']>year:continue
  30:   mi=base['minor'].get((ident,a['year']))
  31:   if base['complete'].get(a['year'],set())!=set(range(11,17)):mi=None
  32:   vals.append(a['stat'].get('IP',0)+(mi or 0))
  33:  return max(vals,default=0)
  34: @functools.lru_cache(None)
  35: def _x(ident,year,rr,calendar):
  36:  rows=hist[ident,'H' if rr=='H' else 'P'];z={'id':ident,'year':year,'role':rr,'x':base['features'](rows,rr,year,ident),'bounded_x':base['features'](rows,rr,year,ident,True)}
  37:  return feature(z,calendar,rows)
  38: def feature(z,calendar=False,rows=None):
  39:  ident,year,rr=z['id'],z['year'],z['role'];rows=rows if rows is not None else z.get('history_override',hist.get((ident,'H' if rr=='H' else 'P'),[]))
  40:  f=np.array(z['bounded_x'],copy=True)
  41:  if calendar:
  42:   by={a['year']:a for a in rows if a['year']<=year};work=[]
  43:   for y in range(year,year-4,-1):
  44:    a=by.get(y);work.append(r.exposure(a['stat'],rr)*(162/60 if y==2020 else 1) if a else 0)
  45:   pos=[a for a in work if a>0];f[:4]=work;f[4]=np.mean(work);f[5]=np.mean(pos) if pos else 0;f[6]=max(pos,default=0);f[7]=min(pos,default=0);f[8]=np.std(work);f[12]=work[0]-work[1];f[28]=f[13]*work[0]/100
  46:   if year==2020:f[15:17]*=162/60
  47:  # Capacity stays raw demonstrated physical work, never synthetic annualized talent.
  48:  f[19:26]=z['x'][19:26]
  49:  if rr=='H':rates=[0.]*7;shares=[0.,0.];cap=0
  50:  else:
  51:   forecast=base['forecast'](rows,rr,year,ident,strict=True);rate=forecast[0] if forecast else old.prior[rr];rates=[rate.get(k,0) for k in ['K','ER','BB','H','QA3','SV','HLD']];shares=[e['minor_share'](ident,first.get(ident)),e['minor_share'](ident,year)];cap=max([a['stat'].get('IP',0)+(base['minor'].get((ident,a['year']),0) if base['complete'].get(a['year'],set())==set(range(11,17)) else 0) for a in rows if a['year']<=year],default=0)
  52:  return np.r_[f,shares,rates,cap,60/162 if year==2020 else 1,int(year-3<=2020<=year),60/162 if first.get(ident)==2020 else 1,int(rr=='SP')]
  53: def xrow(z,h=1,calendar=False):
  54:  f=feature(z,calendar) if 'history_override' in z else _x(z['id'],z['year'],z['role'],calendar)
  55:  return np.r_[f,float(h),f[13]+h]
  56: def training(asof,horizons=(1,),development=False,calendar=False,family='P'):
  57:  roles=['H'] if family=='H' else ['SP','RP'];out=[]
  58:  for rr in roles:
  59:   for z in records[rr]:
  60:    if z['id']%5==0:continue
  61:    for h in horizons:
  62:     ty=z['year']+h
  63:     if ty>min(asof,2025) or (not calendar and (z['year']==2020 or ty==2020)):continue
  64:     t=target(z,h);actual=t['stat'] if t else {};factor=162/60 if calendar and ty==2020 else 1
  65:     weight=60/162 if calendar and ty==2020 else 1
  66:     if family=='H':
  67:      raw=actual.get('PA',0);value=raw*factor;state=0 if not raw else 2 if value>=400 else 1;info=None
  68:     else:
  69:      raw=actual.get('IP',0);info=counts(z['id'],ty)
  70:      if raw and info is None:continue
  71:      state=0 if not raw else 2 if info['GP'] and info['GS']/info['GP']>=.5 else 1;value=raw*factor
  72:     out.append({'z':z,'h':h,'year':ty,'value':value,'raw_value':raw,'weight':weight,'state':state,'info':info,'factor':factor,'actual':actual,'calibration':z['id']%5==4})
  73:  return out
  74: def calibrated_prob(model,X):
  75:  p=model['classifier'].predict_proba(X);full=np.zeros((len(X),3))
  76:  for j,c in enumerate(model['classifier'].classes_):full[:,int(c)]=p[:,j]
  77:  cal=model.get('calibrator')
  78:  if cal is None:return full
  79:  cp=cal.predict_proba(np.log(np.clip(full,1e-6,1)));out=np.zeros_like(full)
  80:  for j,c in enumerate(cal.classes_):out[:,int(c)]=cp[:,j]
  81:  return out
  82: def classifier_fit(rows,X):
  83:  core=np.array([not z['calibration'] for z in rows]);lab=np.array([z['state'] for z in rows]);weights=np.array([z['weight'] for z in rows]);clf=HistGradientBoostingClassifier(**settings).fit(X[core],lab[core],sample_weight=weights[core]);cal=None;calrows=~core
  84:  if calrows.sum()>=100 and len(set(lab[calrows]))==3 and min(np.bincount(lab[calrows],minlength=3))>=10:
  85:   p=clf.predict_proba(X[calrows]);full=np.zeros((len(p),3))
  86:   for j,c in enumerate(clf.classes_):full[:,int(c)]=p[:,j]
  87:   cal=LogisticRegression(C=1,max_iter=500,random_state=2309).fit(np.log(np.clip(full,1e-6,1)),lab[calrows],sample_weight=weights[calrows])
  88:  return clf,cal
  89: def regfit(X,y,weights,linear=False):
  90:  if not len(y):return None
  91:  if linear:
  92:   a=make_pipeline(StandardScaler(),Ridge(alpha=100));a.fit(X,y,ridge__sample_weight=weights);return a
  93:  return HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X,y,sample_weight=weights)
  94: def prediction(reg,X,low=0,high=np.inf):return np.clip(reg.predict(X),low,high) if reg else np.zeros(len(X))
  95: def historical_baseline(z,h=1):
  96:  f=base['forecast'](hist[z['id'],'H' if z['role']=='H' else 'P'],z['role'],z['year'],z['id'],strict=True)
  97:  if f is None:return None
  98:  if h==1:return base['project'](f,z['role'],z['x'][13],z['year'],True)
  99:  # Extend the existing as-of cohort calculation to direct horizons; no final-source curve.
 100:  rr=z['role'];age=round(z['x'][13]);year=z['year'];rates,work=f;pool=[]
 101:  for a in old.AN:
 102:   if a['role']!=rr or a['id']%5==0 or a['year']+h>year or a['year']==2020 or a['year']+h==2020:continue
 103:   ag=r.age_at(a['id'],a['year']);ex=r.exposure(a['stat'],rr)
 104:   if ag is None or abs(ag-age)>4 or ex<(250 if rr=='H' else 80 if rr=='SP' else 30):continue
 105:   b=lookup.get((a['id'],a['year']+h,'H' if rr=='H' else 'P'));pool.append((a['stat'],b['stat'] if b else {}))
 106:  if not pool:return None
 107:  total=sum(r.exposure(a,rr) for a,b in pool);after=sum(r.exposure(b,rr) for a,b in pool);ratio=after/total if total else 0;support=len(pool)/(len(pool)+40);result={}
 108:  for k,val in rates.items():
 109:   before=sum(a.get(k,0) for a,b in pool)/total if total else 0;future=sum(b.get(k,0) for a,b in pool)/after if after else 0;aging=1 if k in ['PA','IP','AB'] else max(0,1+support*((future/before if before else 1)-1));result[k]=val*work*ratio*aging
 110:  if rr=='H':return v.reconcile(result)
 111:  for k in ['SV','HLD']:result[k]=min(result.get(k,0),rates.get(k,0)*work*ratio)
 112:  result['QA3']=min(result.get('QA3',0),result.get('IP',0)/5);return result
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/past_only_followup.py
```python
   1: """Fixed chronology correction: past-only ability priors and stream-correct debut flag."""
   2: import joint_model as j, principal_followup as pmod, hitter_model as hm
   3: from principal_followup import *
   4: original_xrow=j.xrow
   5: @functools.lru_cache(None)
   6: def prior_at(rr,year):
   7:  xs=[a for a in old.AN if a['role']==rr and a['id']%5!=0 and a['year']<=min(year,2025) and a['year']!=2020];total=sum(r.exposure(a['stat'],rr) for a in xs)
   8:  return {k:sum(a['stat'].get(k,0) for a in xs)/total if total else 0 for k in old.fields[rr]}
   9: def past_xrow(z,h=1,calendar=False):
  10:  x=original_xrow(z,h,calendar).copy();ident,year,rr=z['id'],z['year'],z['role'];rows=z.get('history_override',hist.get((ident,'H' if rr=='H' else 'P'),[]))
  11:  if rr=='H':
  12:   firstH=min([a['year'] for a in rows if a['year']<=year and a['stat'].get('PA',0)>0],default=None);x[41]=60/162 if firstH==2020 else 1
  13:  else:
  14:   past=[a for a in rows if year-3<=a['year']<=year and a['role']==rr and a['stat'].get('IP',0)>0];prior=prior_at(rr,year);mass=sum({year-3:.1,year-2:.2,year-1:.3,year:.4}[a['year']] for a in past)
  15:   if mass:
  16:    weighted=[(a['stat'],{year-3:.1,year-2:.2,year-1:.3,year:.4}[a['year']]/mass) for a in past];ex=sum(a['IP']*w for a,w in weighted);rates={k:(sum(a.get(k,0)*w for a,w in weighted)+30*prior.get(k,0))/(ex+30) for k in prior}
  17:   else:rates=prior
  18:   x[31:38]=[rates.get(k,0) for k in ['K','ER','BB','H','QA3','SV','HLD']]
  19:  return x
  20: j.xrow=pmod.xrow=hm.xrow=past_xrow
  21: 
  22: def run():
  23:  cases=read(OUT/'Principal_Cases.json.gz');extras=read(OUT/'Principal_Additional_Cases.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases+extras};manifest=[]
  24:  for year in sorted({z['anchor'] for z in cases+extras}):
  25:   model=pmod.augment(j.fit_pitch(year));joblib.dump(model,OUT/f'past-pitch-{year}.joblib',compress=3);manifest.append(model['manifest']);xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in by];ps=pmod.predict_augmented(model,xs)
  26:   for z,p in zip(xs,ps):
  27:    q=by[z['id'],year,z['role']];q['past_only']=category_stats(q['baseline'],p)|{'GS':p['GS'],'RA':p['RA']};q['components']['past_only']=p
  28:   print('Past-only pitching completed',year,flush=True)
  29:  original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
  30:  for z in original:
  31:   q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline'];q['past_only']=category_stats(z['baseline'],q['components']['past_only']);q['principal_QA3']=category_stats(z['baseline'],q['components']['principal_QA3']);frozen.append(q)
  32:  save('Past_Only_Pitch_Validation.json',{'expanded':scores(cases,['baseline','linear_SP','principal_QA3','past_only']),'frozen94':scores(frozen,['baseline','principal_QA3','past_only']),'additional':scores(extras,['baseline','principal_QA3','past_only']),'manifests':manifest,'scope':'Past-only ability prior excludes holdout IDs and post-anchor seasons. Frozen baseline and comparison category-rate normalization retained for comparability; not newly fitted past-only category/valuation baseline. Fixed correction, not test-selected.'});save('Past_Only_Pitch_Cases.json.gz',cases);save('Past_Only_Pitch_Additional.json.gz',extras)
  33:  hc=read(OUT/'Hitter_Cases.json.gz');he=read(OUT/'Hitter_Additional_Cases.json.gz');byH={(z['mlbam_id'],z['anchor']):z for z in hc+he};manH=[]
  34:  for year in sorted({z['anchor'] for z in hc+he}):
  35:   model=hm.fit_hitter(year);joblib.dump(model,OUT/f'past-hitter-{year}.joblib',compress=3);manH.append(model['manifest']);xs=[z for z in records['H'] if z['year']==year and (z['id'],year) in byH];ps=hm.predict_hitter(model,xs)
  36:   for z,p in zip(xs,ps):q=byH[z['id'],year];q['past_only']=hm.statscale(q['baseline'],p);q['components']['past_only']=p
  37:   print('Stream-correct hitter completed',year,flush=True)
  38:  standard=[z for z in he if z['anchor']+1!=2020];save('Past_Only_Hitter_Validation.json',{'preserved':hm.scores(hc,['baseline','selected','hitter_selected','past_only']),'combined_standard':hm.scores(hc+standard,['baseline','selected','hitter_selected','past_only']),'additional':hm.scores(he,['baseline','hitter_selected','past_only']),'manifest':manH,'scope':'H debut-season calendar flag now uses observed H stream rather than pitching debut mapping; no future first-pitching year leaks into H features.'});save('Past_Only_Hitter_Cases.json.gz',hc);save('Past_Only_Hitter_Additional.json.gz',he)
  39:  if '--current' in sys.argv:
  40:   for horizons,tag in [((1,),'one'),(tuple(range(1,9)),'eight')]:
  41:    pm=pmod.augment(j.fit_pitch(2026,horizons));hh=hm.fit_hitter(2026,horizons);joblib.dump(pm,OUT/f'past-current-pitch-{tag}.joblib',compress=3);joblib.dump(hh,OUT/f'past-current-hitter-{tag}.joblib',compress=3)
  42:   print('Past-only current models saved',flush=True)
  43: if __name__=='__main__':run()
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/joint_model.py
```python
   1: """General role/appearance/depth model; future states are labels, never inputs."""
   2: from shared import *
   3: import joblib
   4: VARIANTS=['joint_raw','joint_calibrated','joint_linear_depth','joint_calendar']
   5: def fit_pitch(asof,horizons=(1,),development=False,calendar=False):
   6:  rows=training(asof,horizons,development,calendar,'P');X=np.stack([xrow(z['z'],z['h'],calendar) for z in rows]);clf,cal=classifier_fit(rows,X)
   7:  use=np.array([not z['calibration'] or not development for z in rows]);weights=np.array([z['weight'] for z in rows]);labels=np.array([z['state'] for z in rows]);countregs={};depth={};linear={};qa={};caps={}
   8:  for state in [1,2]:
   9:   mask=use&(labels==state)
  10:   for key in ['GS','RA']:
  11:    vals=np.array([(z['info'][key]*z['factor'] if z['info'] else 0) for z in rows]);countregs[state,key]=regfit(X[mask],vals[mask],weights[mask]);caps[key]=max(caps.get(key,0),float(np.quantile(vals[mask],.995)))
  12:  for kind in ['SP','RP']:
  13:   mask=np.array([bool(z['info'] and z['info']['GP']>0 and ((z['info']['GS']==z['info']['GP'] and z['info']['GS']>=3) if kind=='SP' else z['info']['GS']==0)) for z in rows])&use
  14:   vals=np.array([z['raw_value']/z['info']['GP'] if z['info'] and z['info']['GP'] else 0 for z in rows]);w=np.array([min(30,z['info']['GP']) if z['info'] else 0 for z in rows])*weights
  15:   depth[kind]=regfit(X[mask],vals[mask],w[mask]);linear[kind]=regfit(X[mask],vals[mask],w[mask],True);caps[kind+'_depth']=float(np.quantile(vals[mask],.995));caps[kind+'_n']=int(mask.sum())
  16:   qmask=mask&np.array([bool(z['info'] and z['info']['exact_QA3_available']) for z in rows]);q=np.array([z['info']['QA3']/z['info']['GP'] if z['info'] and z['info']['QA3'] is not None and z['info']['GP'] else 0 for z in rows]);qa[kind]=regfit(X[qmask],q[qmask],w[qmask]);caps[kind+'_QA3_n']=int(qmask.sum())
  17:  model={'classifier':clf,'calibrator':cal,'counts':countregs,'depth':depth,'linear':linear,'qa':qa,'caps':caps,'calendar':calendar,'asof':asof,'horizons':list(horizons),'manifest':{'asof':asof,'latest_target':max(z['year'] for z in rows),'horizon_support':{str(h):sum(z['h']==h for z in rows) for h in horizons},'classifier_ID_mods':[1,2,3],'calibration_ID_mods':[4],'regressor_ID_mods':[1,2,3] if development else [1,2,3,4],'training_rows':len(rows),'calendar_target_weights':'actual2020 confidence60/162' if calendar else '2020 anchor/target excluded','pure_role_support':caps}}
  18:  return model
  19: def predict_pitch(model,zs,h=1,variant='joint_calibrated'):
  20:  X=np.stack([xrow(z,h,model['calendar']) for z in zs]);prob=calibrated_prob(model,X)
  21:  if variant=='joint_raw':prob=calibrated_prob(model|{'calibrator':None},X)
  22:  regs=model['linear'] if variant=='joint_linear_depth' else model['depth'];caps=model['caps'];sd=prediction(regs['SP'],X,0,caps['SP_depth']);rd=prediction(regs['RP'],X,0,caps['RP_depth']);sq=prediction(model['qa']['SP'],X,0,1);rq=prediction(model['qa']['RP'],X,0,1);sq=np.minimum(sq,sd/5);rq=np.minimum(rq,rd/5)
  23:  means={'IP':np.zeros(len(zs)),'GS':np.zeros(len(zs)),'RA':np.zeros(len(zs)),'QA3':np.zeros(len(zs))}
  24:  conditional={}
  25:  for state in [1,2]:
  26:   gs=prediction(model['counts'][state,'GS'],X,0,caps['GS']);ra=prediction(model['counts'][state,'RA'],X,0,caps['RA']);bad=(gs<ra) if state==2 else (gs>ra);avg=(gs+ra)/2;gs=np.where(bad,avg,gs);ra=np.where(bad,avg,ra)
  27:   ip=gs*sd+ra*rd;q=gs*sq+ra*rq;conditional[state]={'GS':gs,'RA':ra,'IP':ip,'QA3':q}
  28:   for k in means:means[k]+=prob[:,state]*conditional[state][k]
  29:  means['QA3']=np.minimum(means['QA3'],means['IP']/5)
  30:  return [{**{k:float(v[i]) for k,v in means.items()},'probabilities':{'absent':float(prob[i,0]),'RP':float(prob[i,1]),'SP':float(prob[i,2])},'IP_per_start':float(sd[i]),'IP_per_relief':float(rd[i]),'QA3_per_start':float(sq[i]),'QA3_per_relief':float(rq[i]),'conditional':{str(l):{k:float(v[i]) for k,v in d.items()} for l,d in conditional.items()},'capacity_feature':float(X[i,38]),'horizon':h} for i in range(len(zs))]
  31: def category_stats(baseline,pred):
  32:  f=pred['IP']/baseline['IP'] if baseline.get('IP') else 0;out={k:v*f for k,v in baseline.items()};out['IP']=pred['IP'];out['QA3']=pred['QA3']
  33:  for k in ['SV','HLD']:out[k]=baseline.get(k,0)*min(1,f)
  34:  return out
  35: def scores(cases,methods):
  36:  out={}
  37:  for group in sorted({g for z in cases for g in z['groups']}):
  38:   xs=[z for z in cases if group in z['groups']];out[group]={'n':len(xs),'metrics':{}}
  39:   for k in ['IP','K','QA3','ER','BB','H','SV','HLD','GS','RA']:
  40:    out[group]['metrics'][k]={}
  41:    for method in methods:
  42:     valid=[z for z in xs if method in z and k in z[method] and (k in z['actual'] or z.get('actual_absent',not z['actual']))]
  43:     if valid:out[group]['metrics'][k][method]=metric([(z[method][k],z['actual'].get(k,0)) for z in valid])
  44:  return out
  45: def extra_groups(z):
  46:  f=z['x'];g=[]
  47:  if f[0]==0:g.append('returning_after_missed_season')
  48:  if f[13]<=26 and f[0]<100 and f[20]>0:g.append('young_promotion_capacity')
  49:  if f[13]<=26 and z['role']=='SP':g.append('young_SP')
  50:  if f[13]>26 and z['role']=='SP':g.append('established_SP')
  51:  if f[26]:g.append('observed_role_transition')
  52:  return g
  53: def run_one_year():
  54:  prior=read(PARENT/'Quality_Aware_Cases.json.gz');linear_cases=read(PARENT/'Conditional_SP_Cases.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in prior};line={(z['mlbam_id'],z['anchor'],z['role']):z for z in linear_cases};dev={v:[] for v in VARIANTS};man=[]
  55:  for year in [2016,2017,2018,2021,2022]:
  56:   xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  57:   models={False:fit_pitch(year,development=True),True:fit_pitch(year,development=True,calendar=True)}
  58:   for variant in VARIANTS:
  59:    model=models[variant=='joint_calendar'];pred=predict_pitch(model,xs,variant=variant)
  60:    for z,p in zip(xs,pred):
  61:     b=historical_baseline(z);actual=(target(z) or {}).get('stat',{});st=category_stats(b,p);dev[variant].append({'role':z['role'],'prediction':st,'actual':actual})
  62:   print('Joint development completed',year,flush=True)
  63:  development={vv:{rr:{k:metric([(z['prediction'][k],z['actual'].get(k,0)) for z in dev[vv] if z['role']==rr]) for k in ['IP','K','QA3']} for rr in ['SP','RP']} for vv in VARIANTS}
  64:  objective={vv:sum((development[vv][rr]['IP']['MAE']+.25*abs(development[vv][rr]['IP']['bias']))/(150 if rr=='SP' else 50)+.2*development[vv][rr]['K']['MAE']/(150 if rr=='SP' else 50)+.2*development[vv][rr]['QA3']['MAE']/(15 if rr=='SP' else 1) for rr in ['SP','RP']) for vv in VARIANTS};chosen=min(VARIANTS,key=lambda x:objective[x]);save('Development_Selection.json',{'scores':development,'objective':objective,'selected':chosen,'selection':'Development only; no incumbent dominance inferred'});print('Selected joint development',chosen,objective,flush=True)
  65:  cases=[];extra=[]
  66:  for year in [2014,2015,2016,2017,2018,2020,2021,2022,2023,2024]:
  67:   models={False:fit_pitch(year),True:fit_pitch(year,calendar=True)}
  68:   for cal,model in models.items():man.append(model['manifest']);joblib.dump(model,OUT/f'pitch-model-{year}-{int(cal)}.joblib',compress=3)
  69:   xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and z['id']%5==0 and (z['positive_anchor'] or z['x'][0]==0)]
  70:   predictions={vv:predict_pitch(models[vv=='joint_calendar'],xs,variant=vv) for vv in VARIANTS}
  71:   for i,z in enumerate(xs):
  72:    key=z['id'],year,z['role'];q=copy.deepcopy(by[key]) if key in by else {'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':z['role'],'groups':z['groups'],'actual':(target(z) or {}).get('stat',{}),'baseline':historical_baseline(z)}
  73:    if q['baseline'] is None:continue
  74:    q['actual_absent']=not q['actual'];q['groups']=list(dict.fromkeys(q['groups']+extra_groups(z)));info=counts(z['id'],year+1);q['actual']=q['actual']|({'GS':info['GS'],'RA':info['RA']} if info else {'GS':0,'RA':0} if not q['actual'] else {})
  75:    if key in line:q['linear_SP']=line[key]['linear_SP']
  76:    q['components']={vv:predictions[vv][i] for vv in VARIANTS}
  77:    for vv in VARIANTS:q[vv]=category_stats(q['baseline'],predictions[vv][i])|{'GS':predictions[vv][i]['GS'],'RA':predictions[vv][i]['RA']}
  78:    q['joint_selected']=q[chosen]
  79:    if key in by:cases.append(q)
  80:    else:extra.append(q)
  81:   print('Joint test completed',year,len(cases),len(extra),flush=True)
  82:  assert len(cases)==1084 and {(z['mlbam_id'],z['anchor'],z['role']) for z in cases}==set(by)
  83:  original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
  84:  for z in original:
  85:   q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  86:   for vv in [*VARIANTS,'joint_selected']:q[vv]=category_stats(z['baseline'],q['components'][chosen if vv=='joint_selected' else vv])
  87:   for vv in ['selected','role_aware','linear_SP']:
  88:    ratio=q[vv]['IP']/z['baseline']['IP'];q[vv]={k:v*ratio for k,v in z['baseline'].items()}
  89:   frozen.append(q)
  90:  methods=['baseline','selected','role_aware','linear_SP',*VARIANTS,'joint_selected'];result={'selected':chosen,'expanded':scores(cases,methods),'frozen94':scores(frozen,methods),'additional':scores(extra,['baseline',*VARIANTS,'joint_selected']),'manifests':man,'cases':1084,'additional_cases':len(extra),'scope':'Exploratory exposed historical labels. Calendar target2020 confidence weighted, role labels never input.'}
  91:  save('Joint_Validation.json',result);save('Joint_Cases.json.gz',cases);save('Joint_Additional_Cases.json.gz',extra)
  92:  for g in ['all','SP','RP','first_MLB_season','second_MLB_season']:print(g,{k:round(v['MAE'],3) for k,v in result['expanded'][g]['metrics']['IP'].items()},flush=True)
  93: if __name__=='__main__':run_one_year()
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/hitter_model.py
```python
   1: """Chronological hitter extension with shared schedule features; preserve old results."""
   2: from shared import *
   3: import joblib
   4: H_VARIANTS=['calendar_hurdle','calendar_mix_tree','calendar_mix_linear']
   5: def fit_hitter(asof,horizons=(1,),development=False):
   6:  rows=training(asof,horizons,development,True,'H');X=np.stack([xrow(z['z'],z['h'],True) for z in rows]);clf,cal=classifier_fit(rows,X);use=np.array([not z['calibration'] or not development for z in rows]);y=np.array([z['value'] for z in rows]);w=np.array([z['weight'] for z in rows]);lab=np.array([z['state'] for z in rows]);regs={}
   7:  for state in [1,2]:
   8:   mask=use&(lab==state);regs[state]=regfit(X[mask],y[mask],w[mask])
   9:  mask=use&(lab==2);linear=regfit(X[mask],y[mask],w[mask],True);mask=use&(lab>0);hurdle=regfit(X[mask],y[mask],w[mask]);cap=float(np.quantile(y[use&(y>0)],.995))
  10:  return {'classifier':clf,'calibrator':cal,'regs':regs,'linear':linear,'hurdle':hurdle,'cap':cap,'asof':asof,'horizons':list(horizons),'calendar':True,'manifest':{'asof':asof,'latest_target':max(z['year'] for z in rows),'horizon_support':{str(h):sum(z['h']==h for z in rows) for h in horizons},'classifier_ID_mods':[1,2,3],'calibration_ID_mods':[4],'regressor_ID_mods':[1,2,3] if development else [1,2,3,4],'training_rows':len(rows),'target2020_confidence_weight':60/162}}
  11: def predict_hitter(model,zs,h=1,variant='calendar_hurdle'):
  12:  X=np.stack([xrow(z,h,True) for z in zs]);p=calibrated_prob(model,X);regular=prediction(model['linear'] if variant=='calendar_mix_linear' else model['regs'][2],X,400,model['cap']);part=prediction(model['regs'][1],X,0,400);cond=prediction(model['hurdle'],X,0,model['cap']);pa=(1-p[:,0])*cond if variant=='calendar_hurdle' else p[:,1]*part+p[:,2]*regular
  13:  return [{'PA':float(pa[i]),'probabilities':{'absent':float(p[i,0]),'part_time':float(p[i,1]),'regular':float(p[i,2])},'conditional_PA':float(cond[i]),'conditional_regular_PA':float(regular[i]),'conditional_part_PA':float(part[i]),'horizon':h} for i in range(len(zs))]
  14: def statscale(b,p):return v.reconcile({k:value*p['PA']/b['PA'] for k,value in b.items()})
  15: def groups(z):
  16:  f=z['x'];g=[]
  17:  if f[0]==0:g.append('returning_after_missed_season')
  18:  if f[13]<=26 and f[14]<=2:g.append('young_first_full_opportunity')
  19:  if 100<=f[0]<400:g.append('part_time_opportunity_candidate')
  20:  return g
  21: def scores(cases,methods):
  22:  out={}
  23:  for g in sorted({g for z in cases for g in z['groups']}):
  24:   xs=[z for z in cases if g in z['groups']];out[g]={'n':len(xs),'players':len({z['mlbam_id'] for z in xs}),'metrics':{}}
  25:   for k in ['PA','AB','H','HR','TB','R','RBI','BB','SB']:
  26:    out[g]['metrics'][k]={}
  27:    for method in methods:
  28:     valid=[z for z in xs if method in z]
  29:     if valid:out[g]['metrics'][k][method]=metric([(z[method].get(k,0),z['actual'].get(k,0)) for z in valid])
  30:  return out
  31: def run():
  32:  existing=[z for z in read(PARENT/'Opportunity_Test_Cases.json.gz') if z['role']=='H'];by={(z['mlbam_id'],z['anchor']):z for z in existing};extraold={(z['mlbam_id'],z['anchor']):z for z in read(PARENT/'Additional_Anchor_Cases.json.gz') if z['role']=='H'};dev={vv:[] for vv in H_VARIANTS};manifest=[]
  33:  for year in [2016,2017,2018,2021,2022]:
  34:   model=fit_hitter(year,development=True);xs=[z for z in records['H'] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  35:   for vv in H_VARIANTS:
  36:    pred=predict_hitter(model,xs,variant=vv)
  37:    for z,p in zip(xs,pred):dev[vv].append((statscale(historical_baseline(z),p),(target(z) or {}).get('stat',{})))
  38:   print('Hitter development completed',year,flush=True)
  39:  d={vv:{k:metric([(a.get(k,0),b.get(k,0)) for a,b in dev[vv]]) for k in ['PA','HR']} for vv in H_VARIANTS};objective={vv:(d[vv]['PA']['MAE']+.25*abs(d[vv]['PA']['bias']))/600+.2*d[vv]['HR']['MAE']/40 for vv in H_VARIANTS};chosen=min(H_VARIANTS,key=lambda vv:objective[vv]);save('Hitter_Development.json',{'selected':chosen,'scores':d,'objective':objective});print('Selected hitter development',chosen,objective,flush=True)
  40:  cases=[];extras=[];prior_method=read(PARENT/'Opportunity_Validation.json')['selected_by_development']['H']
  41:  for year in [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024]:
  42:   model=fit_hitter(year);manifest.append(model['manifest']);joblib.dump(model,OUT/f'hitter-model-{year}.joblib',compress=3);xs=[z for z in records['H'] if z['year']==year and z['id']%5==0 and (z['positive_anchor'] or z['x'][0]==0)];preds={vv:predict_hitter(model,xs,variant=vv) for vv in H_VARIANTS}
  43:   needs=[z for z in xs if (z['id'],year) not in by and (z['id'],year) not in extraold]
  44:   incumbent={}
  45:   if needs:
  46:    originalmodel=base['fit'](base['training']('H',year),prior_method);ps=base['predict'](originalmodel,needs,prior_method,base['cap_at']('H',year))[0];incumbent={z['id']:float(a) for z,a in zip(needs,ps)}
  47:   for i,z in enumerate(xs):
  48:    key=z['id'],year;b=historical_baseline(z)
  49:    if b is None:continue
  50:    q=copy.deepcopy(by[key]) if key in by else {'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':'H','groups':z['groups'],'baseline':b,'actual':(target(z) or {}).get('stat',{})}
  51:    q['groups']=list(dict.fromkeys(q['groups']+groups(z)));q['components']={vv:preds[vv][i] for vv in H_VARIANTS}
  52:    if key not in by:
  53:     pa=extraold[key]['primary'] if key in extraold else incumbent[z['id']];q['selected']=statscale(q['baseline'],{'PA':pa})
  54:    for vv in H_VARIANTS:q[vv]=statscale(q['baseline'],preds[vv][i])
  55:    q['hitter_selected']=q[chosen]
  56:    if year+1==2020:q['groups'].append('unexpected_shortened_target_2020')
  57:    if key in by:cases.append(q)
  58:    else:extras.append(q)
  59:   print('Hitter test completed',year,len(cases),len(extras),flush=True)
  60:  assert len(cases)==682 and {(z['mlbam_id'],z['anchor']) for z in cases}==set(by)
  61:  methods=['baseline','selected',*H_VARIANTS,'hitter_selected'];standard=[z for z in extras if z['anchor']+1!=2020];result={'selected':chosen,'preserved':scores(cases,methods),'additional_standard':scores(standard,methods),'additional_all_with_shock':scores(extras,methods),'combined_standard':scores(cases+standard,methods),'manifest':manifest,'scope':'Additional chronological scoring; previous labels and preprocessing already exposed, not pristine confirmation. Shock2020 scored separately.'}
  62:  # Independently documented prior IL placements are historical diagnostic labels only.
  63:  il=read(PARENT/'Verified_Availability_Checks.json')['sources'];ilby={z['mlbam_id']:z for z in il};subset=[]
  64:  for z in cases+standard:
  65:   placements=ilby.get(z['mlbam_id'],{}).get('placements',[])
  66:   if any(f"{z['anchor']-2}-01-01"<=t['date']<=f"{z['anchor']}-12-31" for t in placements):subset.append(z)
  67:  result['documented_prior_IL']=scores(subset,methods);save('Hitter_Validation.json',result);save('Hitter_Cases.json.gz',cases);save('Hitter_Additional_Cases.json.gz',extras)
  68:  for group in ['all','durable_four_years','aging_33plus']:print(group,{k:round(a['MAE'],2) for k,a in result['combined_standard'][group]['metrics']['PA'].items()},flush=True)
  69: if __name__=='__main__':run()
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/principal_followup.py
```python
   1: """Reuse completed appearance fits; amend QA3 context and conditional workload only."""
   2: from joint_model import *
   3: def augment(model,development=False):
   4:  rows=training(model['asof'],model['horizons'],development,model['calendar'],'P');use=np.array([not z['calibration'] or not development for z in rows]);X=np.stack([xrow(z['z'],z['h'],model['calendar']) for z in rows]);labels=np.array([z['state'] for z in rows]);weights=np.array([z['weight'] for z in rows]);qmask=np.array([bool(z['info'] and z['info']['GP']>0 and z['info']['GS']==0 and z['info']['exact_QA3_available']) for z in rows])&use
   5:  # Exact rare relief QA3 observed totals; raw GP retains actual evidence weight.
   6:  count=sum(z['info']['QA3'] for i,z in enumerate(rows) if qmask[i]);gp=sum(z['info']['GP'] for i,z in enumerate(rows) if qmask[i]);rpq=count/gp if gp else 0;startregs={};direct={};support={}
   7:  for state in [1,2]:
   8:   mask=use&(labels==state)&np.array([bool(z['info'] and z['info']['GS']>0 and z['info']['exact_QA3_available']) for z in rows]);ys=np.array([max(0,min(1,(z['info']['QA3']-z['info']['RA']*rpq)/z['info']['GS'])) if z['info'] and z['info']['GS'] and z['info']['QA3'] is not None else 0 for z in rows]);w=np.array([z['info']['GS'] if z['info'] else 0 for z in rows])*weights;startregs[state]=regfit(X[mask],ys[mask],w[mask]);support[state]=int(mask.sum())
   9:   mask=use&(labels==state);values=np.array([z['value'] for z in rows]);direct[state]=regfit(X[mask],values[mask],weights[mask],state==2)
  10:  model=copy.copy(model);model['principal_QA3']={'start':startregs,'relief_probability':rpq,'start_training_rows':support,'pure_relief_appearances':gp,'pure_relief_QA3':count};model['direct_conditional']=direct;return model
  11: def predict_augmented(model,zs,h=1,blend=False):
  12:  parts=predict_pitch(model,zs,h,'joint_linear_depth');X=np.stack([xrow(z,h,model['calendar']) for z in zs]);q=model['principal_QA3'];p=calibrated_prob(model,X);startprob={l:prediction(q['start'][l],X,0,1) for l in [1,2]};direct={l:prediction(model['direct_conditional'][l],X) for l in [1,2]};out=[]
  13:  for i,z in enumerate(parts):
  14:   sd=z['IP_per_start'];rd=z['IP_per_relief'];ip=0;qa=0;conds={}
  15:   for l in [1,2]:
  16:    c=z['conditional'][str(l)];gs,ra=c['GS'],c['RA'];ss,rs=sd,rd
  17:    if blend:
  18:     total=.5*c['IP']+.5*direct[l][i]
  19:     if l==2 and gs>0:ss=float(np.clip((total-ra*rd)/gs,0,model['caps']['SP_depth']))
  20:     elif ra>0:rs=float(np.clip((total-gs*sd)/ra,0,model['caps']['RP_depth']))
  21:    ci=gs*ss+ra*rs;cq=gs*min(startprob[l][i],ss/5)+ra*min(q['relief_probability'],rs/5);ip+=p[i,l]*ci;qa+=p[i,l]*cq;conds[str(l)]={**c,'IP':float(ci),'QA3':float(cq),'IP_per_start':ss,'IP_per_relief':rs}
  22:   out.append({**z,'IP':float(ip),'QA3':float(min(qa,ip/5)),'conditional':conds,'QA3_principal_context':True,'conditional_blend':blend})
  23:  return out
  24: def run():
  25:  cases=read(OUT/'Joint_Cases.json.gz');extras=read(OUT/'Joint_Additional_Cases.json.gz');bys={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases+extras};manifest=[]
  26:  for year in sorted({z['anchor'] for z in cases+extras}):
  27:   model=augment(joblib.load(OUT/f'pitch-model-{year}-0.joblib'));joblib.dump(model,OUT/f'principal-model-{year}.joblib',compress=3);manifest.append({'anchor':year,'QA3_offset':model['principal_QA3']['relief_probability'],'QA3_support':model['principal_QA3']['start_training_rows']});xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in bys]
  28:   for method,blend in [('principal_QA3',False),('conditional_blend',True)]:
  29:    pred=predict_augmented(model,xs,blend=blend)
  30:    for z,p in zip(xs,pred):
  31:     q=bys[z['id'],year,z['role']];q[method]=category_stats(q['baseline'],p)|{'GS':p['GS'],'RA':p['RA']};q['components'][method]=p
  32:   print('Principal follow-up',year,flush=True)
  33:  original=read(PARENT.parent/'Historical_Cases.json');by={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
  34:  for z in original:
  35:   q=copy.deepcopy(by[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  36:   for vv in [*VARIANTS,'joint_selected','principal_QA3','conditional_blend']:q[vv]=category_stats(z['baseline'],q['components'][read(OUT/'Joint_Validation.json')['selected'] if vv=='joint_selected' else vv])
  37:   for vv in ['selected','role_aware','linear_SP']:
  38:    f=q[vv]['IP']/z['baseline']['IP'];q[vv]={k:v*f for k,v in z['baseline'].items()}
  39:   frozen.append(q)
  40:  methods=['baseline','selected','role_aware','linear_SP','joint_selected','principal_QA3','conditional_blend'];save('Principal_Validation.json',{'expanded':scores(cases,methods),'frozen94':scores(frozen,methods),'additional':scores(extras,['baseline','joint_selected','principal_QA3','conditional_blend']),'manifest':manifest,'scope':'Fixed exploratory follow-up after initial QA3 failure; blend50/50 not test-selected. QA3 offset is aggregate modeling, not verified component split.'});save('Principal_Cases.json.gz',cases);save('Principal_Additional_Cases.json.gz',extras)
  41:  print(scores(cases,methods)['all']['metrics']['IP'],flush=True);print(scores(cases,methods)['all']['metrics']['QA3'],flush=True)
  42: if __name__=='__main__':run()
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/engine.py
```python
   1: """Research first-year opportunity replacement; no production side effects.
   2: Chronological expert targets already include absence and role attrition. Never
   3: multiply those expected workloads by absence/age a second time.
   4: """
   5: import sys, hashlib, csv
   6: from pathlib import Path
   7: HERE=Path(__file__).resolve().parent
   8: sys.path.insert(0,str(HERE.parent))
   9: import past_only_followup as past
  10: from shared import *
  11: import joblib
  12: from principal_followup import predict_augmented
  13: from hitter_model import predict_hitter
  14: VARIANTS=['appearances','hierarchical','expert_ensemble','joint_ensemble']
  15: P_VARIANTS=VARIANTS+['robust_direct','robust_hurdle','robust_cohort']
  16: 
  17: def put(name,obj):
  18:  b=json.dumps(obj,allow_nan=False,default=lambda a:a.item() if isinstance(a,np.generic) else a).encode()
  19:  (HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
  20: def checkpoint(model,path,compress=3):
  21:  import io
  22:  buffer=io.BytesIO();joblib.dump(model,buffer,compress=compress);payload=buffer.getvalue();assert payload
  23:  joblib.load(io.BytesIO(payload))
  24:  path=Path(path);temporary=path.with_name(path.name+'.tmp');temporary.write_bytes(payload);assert temporary.stat().st_size==len(payload);temporary.replace(path)
  25:  return str(path)
  26: 
  27: def writecsv(name,rows):
  28:  cols=list(dict.fromkeys(k for a in rows for k in a))
  29:  with (HERE/name).open('w',newline='') as f:w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
  30: 
  31: def cohort(z):
  32:  f=z['x'];h=z['role']=='H'
  33:  if f[0]<.6*max(f[1],f[2]) and max(f[1],f[2])>=(400 if h else 100):return 'interrupted'
  34:  if f[13]<=26 and f[14]<=2:return 'young_entry'
  35:  if h:
  36:   if f[11]>=3:return 'durable'
  37:   return 'everyday' if f[0]>=400 else 'part_time'
  38:  if z['role']=='RP':return 'relief_swing'
  39:  return 'stable_rotation' if f[16]>=20 and f[17]>=.8 and f[14]>=3 else 'unstable_rotation'
  40: 
  41: def fx(z):
  42:  f=past.past_xrow(z,1,z['role']=='H');c=cohort(z)
  43:  # Explicit cohort-specific departures from shared age/workload coefficients.
  44:  indicators=np.array([c==s for s in ['stable_rotation','young_entry','interrupted','unstable_rotation','durable','everyday','part_time']],float)
  45:  xs=np.array([f[0],f[1],f[5],f[6],f[11],f[13]-28,f[14],f[16],f[17],f[21],f[25]],float)
  46:  return np.r_[f,indicators,(indicators[:,None]*xs).ravel()]
  47: 
  48: def ridgefit(X,y,w):
  49:  reg=make_pipeline(StandardScaler(),Ridge(alpha=250))
  50:  reg.fit(X,y,ridge__sample_weight=w);return reg
  51: 
  52: def fit(asof,fam):
  53:  rows=[a for a in training(asof,calendar=fam=='H',family=fam) if not a['calibration'] and (fam=='H' or a['z']['role']=='SP')]
  54:  X=np.stack([fx(a['z']) for a in rows]);w=np.array([a['weight'] for a in rows]);y=np.array([a['value'] for a in rows]);labs=np.array([a['state'] for a in rows]);model={'asof':asof,'family':fam,'ridge':ridgefit(X,y,w)}
  55:  # Iteration1: counts learn zero-outcome/role changes, not only surviving starters.
  56:  if fam=='P':
  57:   model['counts']={k:HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X,np.array([a['info'][k] if a['info'] else 0 for a in rows]),sample_weight=w) for k in ['GS','RA']}
  58:  else:
  59:   model['direct']=HistGradientBoostingRegressor(loss='absolute_error',**settings).fit(X,y,sample_weight=w)
  60:  if fam=='P':
  61:   model['robust_direct']=HistGradientBoostingRegressor(loss='absolute_error',**settings).fit(X,y,sample_weight=w)
  62:   active=y>0;model['robust_hurdle']=HistGradientBoostingRegressor(loss='absolute_error',**settings).fit(X[active],y[active],sample_weight=w[active]);model['specialists']={}
  63:   groups=np.array([cohort(a['z']) for a in rows])
  64:   for group in ['stable_rotation','young_entry','interrupted','unstable_rotation']:
  65:    keep=active&(groups==group);n=int(keep.sum())
  66:    if n>=100:model['specialists'][group]=(HistGradientBoostingRegressor(loss='absolute_error',**settings).fit(X[keep],y[keep],sample_weight=w[keep]),n/(n+200))
  67:  model['cap']=float(max(a['raw_value'] for a in rows if a['year']!=2020))
  68:  model['manifest']={'asof':asof,'latest_target':max(a['year'] for a in rows),'rows':len(rows),'fit_ID_mods':sorted({a['z']['id']%5 for a in rows}),'cohorts':dict(__import__('collections').Counter(cohort(a['z']) for a in rows)),'targets_include_zero_outcomes':True,'ridge_alpha':250,'feature_count':X.shape[1],'feature_hash':hashlib.sha256(X.tobytes()).hexdigest(),'target_hash':hashlib.sha256(y.tobytes()).hexdigest()}
  69:  assert model['manifest']['latest_target']<=asof and model['manifest']['fit_ID_mods']==[1,2,3]
  70:  return model
  71: 
  72: def incumbent(asof,fam,zs):
  73:  tag='current-'+('hitter' if fam=='H' else 'pitch')+'-one' if asof==2026 else ('hitter' if fam=='H' else 'pitch')+'-'+str(asof)
  74:  model=joblib.load(OUT/('past-'+tag+'.joblib'))
  75:  return predict_hitter(model,zs) if fam=='H' else predict_augmented(model,zs)
  76: 
  77: def opportunity(model,zs,inc,variant):
  78:  X=np.stack([fx(z) for z in zs]);hier=np.clip(model['ridge'].predict(X),0,model['cap']);fam=model['family'];key='PA' if fam=='H' else 'IP'
  79:  if fam=='H':direct=np.clip(model['direct'].predict(X),0,model['cap']);gs=ra=None
  80:  else:
  81:   gs=np.clip(model['counts']['GS'].predict(X),0,36);ra=np.clip(model['counts']['RA'].predict(X),0,85)
  82:   direct=np.array([a*c['IP_per_start']+b*c['IP_per_relief'] for a,b,c in zip(gs,ra,inc)])
  83:  target=direct if variant=='appearances' else hier if variant=='hierarchical' else .5*(direct+hier) if variant=='expert_ensemble' else .5*(hier+np.array([c[key] for c in inc]))
  84:  if fam=='P' and variant.startswith('robust_'):
  85:   if variant=='robust_direct':target=prediction(model['robust_direct'],X,0,model['cap'])
  86:   else:
  87:    cond=prediction(model['robust_hurdle'],X,0,model['cap'])
  88:    if variant=='robust_cohort':
  89:     for i,z in enumerate(zs):
  90:      specialist=model['specialists'].get(cohort(z))
  91:      if specialist:
  92:       reg,weight=specialist;cond[i]=(1-weight)*cond[i]+weight*prediction(reg,X[i:i+1],0,model['cap'])[0]
  93:    target=cond*np.array([1-c['probabilities']['absent'] for c in inc])
  94:  results=[]
  95:  for i,(z,c,t) in enumerate(zip(zs,inc,target)):
  96:   if fam=='P' and z['role']=='RP':results.append(copy.deepcopy(c));continue
  97:   results.append(reconcile_components(c,float(t),model['cap'],fam,variant,gs[i] if gs is not None else None,ra[i] if ra is not None else None,cohort(z)))
  98:  return results
  99: 
 100: def reconcile_components(c,total,cap,fam,variant,gs=None,ra=None,group=None):
 101:  q=copy.deepcopy(c);q['opportunity_architecture']=variant;q['forecast_cohort']=group;q['expert_unconstrained_workload']=total;q['workload_has_absence_included']=True
 102:  if fam=='H':
 103:   p=q['probabilities'];active=1-p['absent'];desired=min(cap*active,max(0,total));part=q['conditional_part_PA'];reg=q['conditional_regular_PA']
 104:   # Constrained mixture mean: replace incoherent separate active-hurdle forecast.
 105:   # Find a common opportunity shift, retaining role conditional interval bounds.
 106:   lo=-cap;hi=cap
 107:   for _ in range(60):
 108:    d=(lo+hi)/2;a=np.clip(part+d,0,400);b=np.clip(reg+d,400,cap);value=p['part_time']*a+p['regular']*b
 109:    if value<desired:lo=d
 110:    else:hi=d
 111:   d=(lo+hi)/2;part=float(np.clip(part+d,0,400));reg=float(np.clip(reg+d,400,cap))
 112:   q['conditional_part_PA']=part;q['conditional_regular_PA']=reg;q['PA']=p['part_time']*part+p['regular']*reg;q['conditional_PA']=q['PA']/active if active else 0
 113:   q['mixture_constraint_residual']=q['PA']-total
 114:   return q
 115:  # Forecast total already includes attrition. Conditional components are a
 116:  # constrained allocation for audit, not another probability discount.
 117:  p=q['probabilities'];states=q['conditional'];initial=sum(p['RP' if s=='1' else 'SP']*a['IP'] for s,a in states.items())
 118:  factor=max(0,total)/initial if initial else 0
 119:  for s,a in states.items():
 120:   a['GS']=min(36,a['GS']*factor);a['RA']=min(85-a['GS'],a['RA']*factor)
 121:   depth=a['IP_per_start'];relief=a['IP_per_relief'];a['IP']=a['GS']*depth+a['RA']*relief
 122:   # Principal-state QA3 rate preserved, rescaled by appearances and bounded.
 123:   a['QA3']=min(a['IP']/5,a['GS']+a['RA'],a['QA3']*factor)
 124:  for key in ['IP','GS','RA','QA3']:q[key]=sum(p['RP' if s=='1' else 'SP']*a[key] for s,a in states.items())
 125:  q['unconditional_start_expert']=float(gs);q['unconditional_relief_expert']=float(ra);q['mixture_constraint_residual']=q['IP']-total
 126:  return q
 127: 
 128: def stats(b,c,rr,z=None,mixture_leverage=True):
 129:  key='PA' if rr=='H' else 'IP';ratio=c[key]/b[key] if b[key]>0 else 0;s={k:val*ratio for k,val in b.items()}
 130:  if b[key]<=0 and z is not None:
 131:   rows=z.get('history_override',hist.get((z['id'],'H' if rr=='H' else 'P'),[]));prior=past.prior_at(rr,z['year']);xs=[a for a in rows if z['year']-3<=a['year']<=z['year'] and r.exposure(a['stat'],rr)>0];weights=[a['year']-(z['year']-4) for a in xs];mass=sum(weights);ex=sum(r.exposure(a['stat'],rr)*w for a,w in zip(xs,weights))/mass if mass else 0;strength=100 if rr=='H' else 30
 132:   rates={k:((sum(a['stat'].get(k,0)*w for a,w in zip(xs,weights))/mass if mass else 0)+strength*prior.get(k,0))/(ex+strength) for k in old.fields[rr]};s={k:val*c[key] for k,val in rates.items()}
 133:  s[key]=c[key]
 134:  if rr=='H':return v.reconcile(s)
 135:  s['QA3']=c['QA3'];s['GS']=c['GS'];s['RA']=c['RA']
 136:  for k in ['SV','HLD']:
 137:   s[k]=b.get(k,0)*min(1,ratio)
 138:   if mixture_leverage and b[key]>0 and 'conditional' in c and 'probabilities' in c:s[k]=sum(c['probabilities']['RP' if state=='1' else 'SP']*b.get(k,0)*min(1,part['IP']/b[key]) for state,part in c['conditional'].items())
 139:  return s
 140: 
 141: def assert_coherent(c,s,rr,cap):
 142:  p=c['probabilities'];assert abs(sum(p.values())-1)<1e-8 and min(p.values())>=0
 143:  assert all(math.isfinite(a) and a>=-1e-7 for a in s.values())
 144:  if rr=='H':
 145:   assert s['HR']<=s['H']+1e-7 and s['H']<=s['AB']+1e-7 and s['AB']<=s['PA']+1e-7
 146:   assert s['AB']+s['BB']+s['HBP']+s['SF']<=s['PA']+1e-7
 147:   assert s['H']+3*s['HR']<=s['TB']+1e-7 and s['TB']<=4*s['H']+1e-7
 148:   assert c['conditional_regular_PA']<=cap+1e-7
 149:   expected=p['part_time']*c['conditional_part_PA']+p['regular']*c['conditional_regular_PA'];assert abs(expected-s['PA'])<1e-7
 150:  else:
 151:   assert s['QA3']<=s['IP']/5+1e-7
 152:   for a in c['conditional'].values():assert a['GS']<=36+1e-7 and a['GS']+a['RA']<=85+1e-7
 153:   assert abs(sum(p['RP' if k=='1' else 'SP']*a['IP'] for k,a in c['conditional'].items())-s['IP'])<1e-7
 154: 
 155: class FirstYearForecastEngine:
 156:  """Callable research adapter. Load frozen selection and fitted model files."""
 157:  def __init__(self,artifact_dir=HERE):
 158:   folder=Path(artifact_dir);self.selection=json.loads((folder/'Selection_Freeze.json').read_text())['selected'];self.models={fam:joblib.load(folder/f'current-{fam}.joblib') for fam in ['P','H']}
 159:  def predict(self,zs):
 160:   result=[]
 161:   for z in zs:
 162:    fam='H' if z['role']=='H' else 'P';c=incumbent(2026,fam,[z]);variant=self.selection[fam]
 163:    result.extend(c if variant=='incumbent' else opportunity(self.models[fam],[z],c,variant))
 164:   return result
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/roster-opportunity/engine.py
```python
   1: """Own role/opportunity forecasts. Public forecasts are evaluation-only.
   2: Separate per-appearance depth, role/opportunity counts, and probability of MLB
   3: participation. Missing medical evidence is never interpreted as health.
   4: """
   5: import sys
   6: from pathlib import Path
   7: HERE=Path(__file__).resolve().parent
   8: sys.path.insert(0,str(HERE.parent/'first-year-repair'))
   9: import importlib.util
  10: _spec=importlib.util.spec_from_file_location("prior_repair_engine",HERE.parent/"first-year-repair"/"engine.py")
  11: prior=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(prior)
  12: globals().update({k:val for k,val in vars(prior).items() if not k.startswith("_")})
  13: HERE=Path(__file__).resolve().parent
  14: GP={}
  15: for p in json.loads(Path(sys.argv[1]+'/trade-preview-v22/model/career_history_cache.json').read_text())['profiles']:
  16:  for a in p.get('seasons',[]):
  17:   if a['role']=='H':
  18:    n=a.get('skills',{}).get('gamesPlayed',a.get('stat',{}).get('GP'))
  19:    if n is not None:GP[a['id'],a['year']]=float(n)
  20: 
  21: def observed(z):
  22:  h=z['role']=='H';rows=z.get('history_override',hist.get((z['id'],'H' if h else 'P'),[]));by={a['year']:a for a in rows if a['year']<=z['year']};out=[]
  23:  for yr in range(z['year'],z['year']-3,-1):
  24:   a=by.get(yr);s=a['stat'] if a else {};ex=s.get('PA' if h else 'IP',0)
  25:   info=counts(z['id'],yr) if not h else None
  26:   gp=GP.get((z['id'],yr)) if h else ((info or {}).get('GP'))
  27:   gs=None if h else ((info or {}).get('GS'))
  28:   if yr==2026 and not h:gp=float(z['x'][15]);gs=float(z['x'][16])
  29:   fac=162/60 if yr==2020 else 1
  30:   out.append({'ex':ex*fac,'gp':None if gp is None else gp*fac,'gs':None if gs is None else gs*fac})
  31:  return out
  32: 
  33: def decomposition(z):
  34:  h=z['role']=='H';o=observed(z);weights=[3,2,1];good=[(a,w) for a,w in zip(o,weights) if a['gp'] and a['ex']>0]
  35:  if h:
  36:   depth=(sum(a['ex']*w for a,w in good)+20*4.1)/(sum(a['gp']*w for a,w in good)+20) if good else 4.1
  37:   opportunity=max([a['gp'] for a in o if a['gp'] is not None],default=z['x'][0]/depth)
  38:   opportunity=min(162,opportunity);latest=o[0]['gp'];missing=latest is None
  39:  else:
  40:   starters=[(a,w) for a,w in good if a['gs'] and a['gs']/a['gp']>=.8]
  41:   depth=(sum(a['ex']*w for a,w in starters)+5*5.5)/(sum(a['gs']*w for a,w in starters)+5) if starters else 5.5
  42:   opportunity=min(34,max([a['gs'] or 0 for a in o],default=0));latest=o[0]['gs'];missing=latest is None
  43:  return {'depth':float(np.clip(depth,2 if h else 2.5,5.2 if h else 7)), 'healthy_opportunity':float(opportunity),'latest_opportunity':float(latest or 0),'counts_missing':missing,'observations':o}
  44: 
  45: def features(z):
  46:  d=decomposition(z);return np.r_[past.past_xrow(z,1,z['role']=='H'),d['depth'],d['healthy_opportunity'],d['latest_opportunity'],d['counts_missing']]
  47: 
  48: def fit_layer(asof,fam):
  49:  rows=[a for a in training(asof,calendar=fam=='H',family=fam) if not a['calibration'] and (fam=='H' or a['z']['role']=='SP')]
  50:  use=[]
  51:  for a in rows:
  52:   if fam=='H':cnt=a['raw_value']/decomposition(a['z'])['depth']
  53:   else:cnt=(a['info'] or {}).get('GS',0)
  54:   if cnt is not None:use.append((a,cnt*a['factor']))
  55:  X=np.stack([features(a['z']) for a,c in use]);y=np.array([c for a,c in use]);w=np.array([a['weight'] for a,c in use]);active=np.array([a['value']>0 for a,c in use]);out={'asof':asof,'family':fam,'fits':{}}
  56:  for alpha in [100,1000,10000]:
  57:   reg=make_pipeline(StandardScaler(),Ridge(alpha=alpha));reg.fit(X[active],y[active],ridge__sample_weight=w[active]);out['fits'][str(alpha)]=reg
  58:  out['tree']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[active],y[active],sample_weight=w[active])
  59:  # Transparent own usage baseline: completed, disjoint-core empirical expected
  60:  # future count / healthy recent count, shrunken within usage and age bands.
  61:  buckets={}
  62:  for a,c in use:
  63:   d=decomposition(a['z']);k=bucket(a['z']);buckets.setdefault(k,[]).append((c,d['healthy_opportunity']))
  64:  globalratio=sum(c for a,c in use)/max(1,sum(decomposition(a['z'])['healthy_opportunity'] for a,c in use))
  65:  out['retention']={k:(sum(c for c,n in xs)+30*globalratio)/(sum(n for c,n in xs)+30) for k,xs in buckets.items()};out['global_retention']=globalratio
  66:  out['manifest']={'asof':asof,'target_end':max(a['year'] for a,c in use),'core_ID_mods':sorted({a['z']['id']%5 for a,c in use}),'count_rows':len(use),'excluded_missing_count_rows':len(rows)-len(use),'count_target_hash':hashlib.sha256(y.tobytes()).hexdigest(),'medical_cause_labels':False,'H_count_target':'future PA / as-of smoothed PA-per-game; appearance equivalents, not future observed games'}
  67:  return out
  68: 
  69: def bucket(z):
  70:  d=decomposition(z);threshold=120 if z['role']=='H' else 24
  71:  return str(int(d['healthy_opportunity']>=threshold))+':'+str(int(z['x'][13]>=33))
  72: 
  73: def predict_layer(model,zs,inc,variant):
  74:  if variant in {'tree_quarter','tree_half','ridge_quarter','usage_quarter'}:
  75:   method='tree' if variant.startswith('tree') else 'ridge_100' if variant.startswith('ridge') else 'usage';weight=.5 if variant.endswith('half') else .25
  76:   fresh=predict_layer(model,zs,inc,method);result=[]
  77:   for z,c,q in zip(zs,inc,fresh):
  78:    key='PA' if z['role']=='H' else 'IP';total=(1-weight)*c[key]+weight*q[key]
  79:    mixed=reconcile_components(c,total,754 if key=='PA' else 251,'H' if key=='PA' else 'P',variant,q.get('GS',0),q.get('RA',0),cohort(z));mixed['opportunity_layer']=q['opportunity_layer']|{'weight':weight,'incumbent_weight':1-weight};result.append(mixed)
  80:   return result
  81:  h=model['family']=='H';X=np.stack([features(z) for z in zs]);alpha=variant.replace('ridge_','');cap=162 if h else 34
  82:  if variant.startswith('ridge_'):activecounts=np.clip(model['fits'][alpha].predict(X),0,cap)
  83:  elif variant=='tree':activecounts=np.clip(model['tree'].predict(X),0,cap)
  84:  else:activecounts=None
  85:  out=[]
  86:  for i,(z,c) in enumerate(zip(zs,inc)):
  87:   d=decomposition(z);basecount=np.clip(d['healthy_opportunity']*model['retention'].get(bucket(z),model['global_retention']),0,cap)
  88:   active=1-c['probabilities']['absent']
  89:   count=basecount if variant=='usage' else (.5*basecount+.5*float(np.clip(model['fits']['1000'].predict(X[i:i+1])[0],0,cap))*active if variant=='blend' else activecounts[i]*active)
  90:   # Usage baseline already includes zero outcomes; never apply absence again.
  91:   expected=count*d['depth']
  92:   if not h:expected+=c.get('RA',0)*c.get('IP_per_relief',1)
  93:   q=reconcile_components(c,float(expected),754 if h else 251,'H' if h else 'P',variant,float(count),float(c.get('RA',0)),cohort(z))
  94:   q['opportunity_layer']={'expected_appearances':float(count),'healthy_role_appearances':d['healthy_opportunity'],'work_per_appearance':d['depth'],'MLB_participation_probability':active,'medical_availability':'unknown','roster_depth':'not supplied','role_evidence':'demonstrated MLB usage','counts_missing':d['counts_missing'],'zero_outcomes_included_once':True}
  95:   out.append(q)
  96:  return out
  97: 
  98: class EvidenceContract:
  99:  """Dated factual inputs; no current roster backfill into historical anchors."""
 100:  @staticmethod
 101:  def validate(evidence,asof,target_year):
 102:   from datetime import date
 103:   end=date.fromisoformat(asof)
 104:   for e in evidence:
 105:    assert e['source_url'] and e['evidence_kind'] in {'roster','injury','team_usage'}
 106:    assert date.fromisoformat(e['published_date'])<=end
 107:    assert e['target_year']==target_year
 108:    assert e['fact_or_assumption'] in {'verified_fact','explicit_expectation'}
 109:   return evidence
 110:  @staticmethod
 111:  def allocate_team(rows,total):
 112:   # Normalize healthy-role slots before player-specific availability. Team
 113:   # budget is never a player minimum and no missing roster is invented.
 114:   assert total>=0 and all(a['healthy_slots']>=0 for a in rows)
 115:   allocated=np.zeros(len(rows));remaining=float(total);active={i for i,a in enumerate(rows) if a['healthy_slots']>0}
 116:   while active and remaining>1e-9:
 117:    mass=sum(rows[i]['healthy_slots'] for i in active);capped=[];proposal={i:remaining*rows[i]['healthy_slots']/mass for i in active}
 118:    for i in active:
 119:     room=max(0,rows[i].get('max_slots',float('inf'))-allocated[i])
 120:     if proposal[i]>=room:capped.append((i,room))
 121:    if not capped:
 122:     for i,value in proposal.items():allocated[i]+=value
 123:     remaining=0;break
 124:    for i,room in capped:allocated[i]+=room;remaining-=room;active.remove(i)
 125:   return [a|{'allocated_slots':float(allocated[i]),'team_unallocated_slots':remaining} for i,a in enumerate(rows)]
 126: 
 127: def apply_evidence(component,z,evidence,asof):
 128:  """Optional factual opportunity overrides; no forecast source substitution.
 129:  Healthy appearances require a dated team allocation. Verified injuries carry
 130:  no numerical penalty without a separately labeled expected missed count.
 131:  """
 132:  EvidenceContract.validate(evidence,asof,z['year']+1);q=copy.deepcopy(component);layer=q.setdefault('opportunity_layer',{});d=decomposition(z);count=q['PA' if z['role']=='H' else 'IP']/d['depth'];active=1-q['probabilities']['absent'];applied=[]
 133:  for e in evidence:
 134:   if e.get('mlbam_id')!=z['id']:continue
 135:   if e['evidence_kind']=='roster':layer['roster_role_evidence']=e.get('status','dated roster observation')
 136:   if e['evidence_kind']=='roster' and 'allocated_healthy_appearances' in e:
 137:    assert e['fact_or_assumption']=='explicit_expectation' and e.get('team_budget_id')
 138:    count=float(e['allocated_healthy_appearances'])*active;applied.append(e)
 139:   if e['evidence_kind']=='injury':
 140:    layer['verified_injury_status']=e.get('status','documented injury');layer['injury_evidence']='verified current fact; forecast-year timetable missing';applied.append(e)
 141:    if 'expected_unavailable_appearances' in e:
 142:     assert e['fact_or_assumption']=='explicit_expectation';assert e['expected_unavailable_appearances']>=0
 143:     # Cap opportunity to medically available slots, never re-discount expected
 144:     # statistical work by a second generic absence probability.
 145:     count=min(count,max(0,d['healthy_opportunity']-e['expected_unavailable_appearances'])*active)
 146:  total=count*d['depth'];out=reconcile_components(q,total,754 if z['role']=='H' else 251,'H' if z['role']=='H' else 'P','dated_evidence',count,q.get('RA',0),cohort(z));out['opportunity_layer']=layer|{'applied_evidence':applied,'expected_appearances':count};return out
 147: 
 148: class RoleOpportunityEngine:
 149:  def __init__(self,folder=HERE):
 150:   self.folder=Path(folder);self.selection=read(self.folder/'Selection_Freeze.json')['selected'];self.models={f:joblib.load(self.folder/f'current-{f}.joblib') for f in ['P','H']}
 151:  def predict(self,zs,evidence=(),asof='2026-10-09'):
 152:   out=[]
 153:   for z in zs:
 154:    fam='H' if z['role']=='H' else 'P';c=incumbent(2026,fam,[z])[0];method=self.selection[fam]
 155:    q=c if z['role']=='RP' or method=='incumbent' else predict_layer(self.models[fam],[z],[c],method)[0]
 156:    if any(e.get('mlbam_id')==z['id'] for e in evidence):q=apply_evidence(q,z,evidence,asof)
 157:    out.append(q)
 158:   return out
 159: 
 160: @functools.lru_cache(None)
 161: def _incmodel(asof,fam):
 162:  tag='current-'+('hitter' if fam=='H' else 'pitch')+'-one' if asof==2026 else ('hitter' if fam=='H' else 'pitch')+'-'+str(asof)
 163:  return joblib.load(OUT/('past-'+tag+'.joblib'))
 164: def incumbent(asof,fam,zs):
 165:  model=_incmodel(asof,fam)
 166:  return predict_hitter(model,zs) if fam=='H' else predict_augmented(model,zs)
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/roster-opportunity/hybrid.py
```python
   1: """Minimal first-year opportunity adapter; no production or later-year mutation."""
   2: from engine import *
   3: from mean_select import role_group
   4: class HybridForecastEngine:
   5:  def __init__(self,folder=HERE):
   6:   self.folder=Path(folder);self.selection=read(self.folder/'Hybrid_Selection_Freeze.json')['role_choices'];self.count_models={f:joblib.load(self.folder/f'current-{f}.joblib') for f in ['P','H']};self.strong_models={f:joblib.load(HERE.parent/'first-year-repair'/f'current-{f}.joblib') for f in ['P','H']};self.strong_selection=read(HERE.parent/'first-year-repair'/'Selection_Freeze.json')['selected'];self.history_models={}
   7:  def predict(self,zs,evidence=(),asof='2026-10-09',incumbent_components=None):
   8:   out=[]
   9:   for z in zs:
  10:    fam='H' if z['role']=='H' else 'P';asof_year=z['year'];c=copy.deepcopy(incumbent_components[(z['id'],z['year'],z['role'])]) if incumbent_components is not None else incumbent(asof_year,fam,[z])[0];g=role_group(z);method='incumbent' if z['role']=='RP' else self.selection[fam][g]
  11:    if asof_year==2026:count_model=self.count_models[fam];strong_model=self.strong_models[fam]
  12:    else:
  13:     if (asof_year,fam) not in self.history_models:self.history_models[asof_year,fam]=(joblib.load(self.folder/f'test-{fam}-{asof_year}.joblib'),joblib.load(HERE.parent/'first-year-repair'/f'test-{fam}-{asof_year}.joblib'))
  14:     count_model,strong_model=self.history_models[asof_year,fam]
  15:    strong=prior.opportunity(strong_model,[z],[c],self.strong_selection[fam])[0] if z['role']!='RP' else c
  16:    if method=='strong_prior':q=strong
  17:    elif method=='incumbent':q=c
  18:    elif method in {'hybrid_half','hybrid_quarter'}:
  19:     counts=predict_layer(count_model,[z],[c],'tree')[0];key='PA' if fam=='H' else 'IP';weight=.5 if method=='hybrid_half' else .25;q=reconcile_components(c,(1-weight)*strong[key]+weight*counts[key],754 if fam=='H' else 251,fam,'hybrid_half',counts.get('GS',0),counts.get('RA',0),g)
  20:    elif method in {'incumbent_strong_half','incumbent_strong_quarter'}:
  21:     key='PA' if fam=='H' else 'IP';weight=.5 if method=='incumbent_strong_half' else .25;q=reconcile_components(c,weight*strong[key]+(1-weight)*c[key],754 if fam=='H' else 251,fam,method,c.get('GS',0),c.get('RA',0),g)
  22:    else:q=predict_layer(count_model,[z],[c],method)[0]
  23:    if fam=='H' and method=='incumbent':q=reconcile_components(q,q['PA'],754,'H',method,group=g)
  24:    d=decomposition(z);q['hybrid_method']=method;q['role_evidence_group']=g;q.setdefault('opportunity_layer',{}).update({'demonstrated_healthy_opportunity':d['healthy_opportunity'],'observed_latest_opportunity':d['latest_opportunity'],'work_per_appearance':d['depth'],'injury_evidence':'missing','roster_depth_evidence':'missing','opportunity_is_unconditional':True,'no_additional_absence_or_age_discount':True})
  25:    if any(e.get('mlbam_id')==z['id'] for e in evidence):q=apply_evidence(q,z,evidence,asof)
  26:    out.append(q)
  27:   return out
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/roster-opportunity/talent.py
```python
   1: """Rate-engine boundary. Reuse Pipeline's independent existing talent estimate.
   2: This adapter does not recollect Statcast, change prospect translations, or
   3: apply availability to rates. Age adjustments already in the preserved rate
   4: estimate are retained once. New ability research can replace this contract
   5: without retraining organizational opportunity.
   6: """
   7: from dataclasses import dataclass
   8: from engine import stats
   9: @dataclass(frozen=True)
  10: class TalentRateForecast:
  11:  role: str
  12:  preserved_stats: dict
  13:  asof_features: dict
  14:  @property
  15:  def rates_per_opportunity(self):
  16:   key='PA' if self.role=='H' else 'IP';denom=self.preserved_stats.get(key,0)
  17:   return {k:v/denom for k,v in self.preserved_stats.items()} if denom else None
  18:  def project(self,opportunity):
  19:   # The preserved QA3 conditional yields (exact league definition), state
  20:   # appearance bounds, and SV/HLD caps accompany the opportunity components.
  21:   # Scaling cancels the old workload total and preserves its per-unit talent
  22:   # rates. Neither age nor availability is applied again here.
  23:   return stats(self.preserved_stats,opportunity,self.role,self.asof_features)
  24:  @property
  25:  def evidence(self):
  26:   return {'rate_source':'preserved independent Pipeline talent/aging estimate','rate_unit':'PA' if self.role=='H' else 'IP','new_statcast_collection':False,'availability_discount_on_rates':False,'missing_statcast_does_not_become_zero_skill':True}
```

## /workspace/scratch/c9758a03c946/pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/roster-opportunity/integrate.py
```python
   1: from hybrid import *
   2: from talent import TalentRateForecast
   3: from run_helpers import saveout,csvout
   4: import importlib.util
   5: s=importlib.util.spec_from_file_location('preserved_firstyear_valuation',HERE.parent/'first-year-repair'/'current.py');cur=importlib.util.module_from_spec(s);s.loader.exec_module(cur)
   6: def run():
   7:  adapter=HybridForecastEngine();league=read(OUT/'Past_Only_League_Impact.json.gz');evidence=read(HERE/'Current_Evidence.json');output=[];checks={'stats_coherent':0,'future_paths_frozen':0,'state_clips':0,'adapter_replays':0};names={'Paul Skenes','Aaron Judge','Jacob Misiorowski','Nolan McLean','Zack Wheeler','Juan Soto','Matt Olson','Jose Ramirez','Tarik Skubal','Logan Webb','Garrett Crochet','Cade Smith','Freddie Freeman'}
   8:  for a in league:
   9:   q={'id':a['id'],'name':a['name'],'role':a['role'],'status':a['status'],'baseline_values':a['baseline_values']}
  10:   if a['status']!='supported_MLB':q['hybrid_values']=a['baseline_values'];output.append(q);continue
  11:   rr=a['role'];p=old.players[a['id']];rows=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':rows,'x':base['features'](rows,rr,2026,a['mlbam_id']),'bounded_x':base['features'](rows,rr,2026,a['mlbam_id'],True)};c=adapter.predict([z],evidence)[0];b=a['baseline_annual'][0];rates=TalentRateForecast(rr,b,z);st=rates.project(c)
  12:   if rr!='RP':assert_coherent(c,st,rr,754 if rr=='H' else 251)
  13:   else:assert st['QA3']<=st['IP']/5+1e-7
  14:   checks['stats_coherent']+=1;paths,_=m.paths(p);_,audit=v.mlb_role_paths(p,rr);values,clips=cur.value_paths(paths,audit['outcome_state_projections'],b,c,rr);conditional,states=cur.conditional_values(paths,b,c,rr);checks['future_paths_frozen']+=1;checks['state_clips']+=clips
  15:   q.update({'mlbam_id':z['id'],'baseline':b,'hybrid':st,'components':c,'hybrid_values':values,'conditional_value_sensitivity':conditional,'conditional_states':states,'unchanged_later_years':True,'talent_rate_evidence':rates.evidence,'rate_data_scope':'Existing preserved independent talent rates and age normalizers; no newly collected Statcast or invented features'})
  16:   if a['name'] in names:assert adapter.predict([z],evidence)[0]==c;checks['adapter_replays']+=1
  17:   output.append(q)
  18:  for label in ['baseline','hybrid']:
  19:   ranked=sorted(output,key=lambda a:-(a[label+'_values'].get('neutral') or -1e10))
  20:   for n,a in enumerate(ranked,1):a[label+'_rank']=n
  21:  flat=[]
  22:  for a in output:
  23:   x={k:a.get(k) for k in ['id','name','mlbam_id','role','status','baseline_rank','hybrid_rank']};x['rank_change']=a['baseline_rank']-a['hybrid_rank']
  24:   for label in ['baseline','hybrid']:
  25:    x.update({label+'_'+k:val for k,val in a[label+'_values'].items()})
  26:    if label in a:x.update({label+'_'+k:val for k,val in a[label].items()})
  27:   x['neutral_delta']=x['hybrid_neutral']-x['baseline_neutral'] if x['hybrid_neutral'] is not None else None
  28:   if 'components' in a:x.update({'hybrid_method':a['components']['hybrid_method'],'role_evidence_group':a['components']['role_evidence_group'],'absence_probability':a['components']['probabilities']['absent'],'verified_injury_status':a['components']['opportunity_layer'].get('verified_injury_status','not assessed'),'mixture_constraint_residual':a['components'].get('mixture_constraint_residual',0)})
  29:   flat.append(x)
  30:  csvout('League_All_Assets_Before_After.csv',flat);csvout('League_Supported_MLB_Before_After.csv',[a for a in flat if a['status']=='supported_MLB']);csvout('Representative_Before_After.csv',[a for a in flat if a['name'] in names]);saveout('Hybrid_League.json.gz',output);saveout('Hybrid_Integration_Verification.json',{'assets':len(flat),'supported':checks['stats_coherent'],'checks':checks,'no_production_mutations':True,'prospect_branches_and_later_years_frozen':True,'current_evidence_records':len(evidence),'no_external_forecast_inputs':True})
  31:  print('HYBRID INTEGRATED',checks,flush=True)
  32: if __name__=='__main__':run()
```

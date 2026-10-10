"""Targeted expected-mean opportunity repair, independent from production.
All missing observations are represented by status and NaN, never fabricated0.
"""
import sys,importlib.util,copy,hashlib,json,gzip,csv,functools
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'roster-opportunity'))
_spec=importlib.util.spec_from_file_location('preserved_roster_engine',HERE.parent/'roster-opportunity/engine.py');legacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(legacy)
globals().update({k:v for k,v in vars(legacy).items() if not k.startswith('_') and k!='HERE'})
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
HERE=Path(__file__).resolve().parent

def put(name,obj):
 b=json.dumps(obj,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x).encode();(HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def csvout(name,rows):
 with (HERE/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
VERIFIED={}
for year in [2025,2026]:
 for fam,group in [('H','hitting'),('P','pitching')]:
  p=HERE/'verified'/f'{group}{year}.json.gz'
  if p.exists():
   a=read(p)['stats'][0];assert a['totalSplits']==len(a['splits']) and len(a['splits'])<5000
   VERIFIED[year,fam]={s['player']['id']:s for s in a['splits']}

def observation(z,year):
 fam='H' if z['role']=='H' else 'P';ident=z['id'];rows=z.get('history_override',hist.get((ident,fam),[]));by={a['year']:a for a in rows if a['year']<=z['year']};a=by.get(year);debut=min([a['year'] for a in rows if r.exposure(a['stat'],z['role'])>0],default=year)
 if (year,fam) in VERIFIED:
  source=f'official {year} complete regular-season aggregate';s=VERIFIED[year,fam].get(ident)
  if s:
   st=s['stat'];ex=float(st['plateAppearances']) if fam=='H' else float(st.get('outs',0))/3;gp=float(st.get('gamesPlayed',0));gs=float(st.get('gamesStarted',0)) if fam=='P' else None
   return {'year':year,'exposure':ex,'GP':gp,'GS':gs,'status':'observed_positive' if ex>0 else 'verified_zero','complete':True,'source':source,'source_date':'2026-10-10','statistical_cutoff':f'{year} regular-season end','medical_absence':False}
  # Complete source census+verified MLBAM identity establishes no MLB work,
  # not a medical diagnosis. Source failure cannot enter this branch.
  return {'year':year,'exposure':0.,'GP':0.,'GS':0. if fam=='P' else None,'status':'verified_zero','complete':True,'source':source,'source_date':'2026-10-10','statistical_cutoff':f'{year} regular-season end','medical_absence':False}
 if year<debut:return {'year':year,'exposure':None,'GP':None,'GS':None,'status':'not_yet_MLB','complete':True,'source':'verified stream debut','source_date':None,'statistical_cutoff':year,'medical_absence':False}
 if 2010<=year<=2025:
  # Preserved annual source census. Distinguish known absence from missing counts.
  if not a:return {'year':year,'exposure':0.,'GP':0.,'GS':0. if fam=='P' else None,'status':'verified_zero','complete':True,'source':'preserved complete annual MLB census','source_date':None,'statistical_cutoff':year,'medical_absence':False}
  ex=r.exposure(a['stat'],z['role']);ci=counts(ident,year) if fam=='P' else None;gp=GP.get((ident,year)) if fam=='H' else (ci or {}).get('GP');gs=None if fam=='H' else (ci or {}).get('GS')
  return {'year':year,'exposure':float(ex),'GP':gp,'GS':gs,'status':'observed_positive' if ex>0 else 'verified_zero','complete':True,'source':'preserved complete annual MLB census','source_date':None,'statistical_cutoff':year,'medical_absence':False}
 # Current unverified export is insufficient for complete-season interpretation.
 return {'year':year,'exposure':None,'GP':None,'GS':None,'status':'unverified_current' if a else 'missing','complete':False,'source':(a or {}).get('source','not available'),'source_date':None,'statistical_cutoff':None,'medical_absence':False}

def evidence_features(z):
 os=[observation(z,y) for y in range(z['year'],z['year']-4,-1)];h=z['role']=='H';fac=lambda a:162/60 if h and a['year']==2020 else 1
 ex=np.array([np.nan if a['exposure'] is None else a['exposure']*fac(a) for a in os]);positive=ex[np.isfinite(ex)&(ex>0)];f=legacy.past.past_xrow(z,1,h).copy()
 f[:4]=ex;f[4]=float(np.nanmean(ex)) if np.isfinite(ex).any() else np.nan;f[5]=float(positive.mean()) if len(positive) else np.nan;f[6]=float(max(positive)) if len(positive) else np.nan;f[7]=float(min(positive)) if len(positive) else np.nan;f[8]=float(np.nanstd(ex)) if np.isfinite(ex).any() else np.nan;f[9]=len(positive);f[10]=sum(a['status']=='verified_zero' for a in os);f[12]=ex[0]-ex[1];f[28]=f[13]*ex[0]/100
 f[15]=np.nan if os[0]['GP'] is None else os[0]['GP']*fac(os[0]);f[16]=np.nan if os[0]['GS'] is None else os[0]['GS']*fac(os[0])
 if not h:
  f[17]=os[0]['GS']/os[0]['GP'] if os[0]['GP'] else np.nan;f[18]=os[1]['GS']/os[1]['GP'] if os[1]['GP'] else np.nan
 else:f[17:19]=np.nan
 threshold=600 if h else 150 if z['role']=='SP' else 50;run=0
 for year in range(z['year'],z['year']-6,-1):
  a=observation(z,year)
  if a['exposure'] is None:run=np.nan;break
  if a['exposure'] >= threshold*(60/162 if year==2020 else 1):run+=1
  else:break
 f[11]=run
 ds=[]
 for a,w in zip(os[:3],[3,2,1]):
  if a['exposure'] and a['GP'] and (h or (a['GS'] and a['GS']/a['GP']>=.8)):
   ds.append((a['exposure']*fac(a), (a['GP'] if h else a['GS'])*fac(a),w))
 depth=(sum(e*w for e,n,w in ds)+(82 if h else 27.5))/(sum(n*w for e,n,w in ds)+(20 if h else 5));depth=float(np.clip(depth,2 if h else 2.5,5.2 if h else 7))
 counts0=[a['GP'] if h else a['GS'] for a in os[:3]];available=[float(x)*fac(a) for x,a in zip(counts0,os[:3]) if x is not None];capacity=min(162 if h else 34,max(available,default=0));capunknown=not bool(available)
 extras=[depth,capacity,np.nan if counts0[0] is None else counts0[0],capunknown]+[a['exposure'] is None for a in os]+[a['GP'] is None for a in os]+[a['status']=='verified_zero' for a in os]+[a['status']=='not_yet_MLB' for a in os]
 return np.r_[f,extras],{'observations':os,'depth':depth,'healthy_role_capacity':capacity,'capacity_is_medically_verified':False,'capacity_status':'unknown' if capunknown else 'demonstrated full-role scenario','age':f[13]}

def cohort_key(z):
 _,d=evidence_features(z);o=d['observations'];latest=o[0]['exposure'];pastmax=max([a['exposure'] or 0 for a in o[1:3]],default=0)
 if latest is None:return 'unknown'
 if latest<.6*pastmax and pastmax>=(400 if z['role']=='H' else 100):return 'interrupted'
 if z['x'][13]<=26 and z['x'][14]<=2:return 'young'
 if z['role']=='H' and latest>=400:return 'established'
 if z['role']=='SP' and o[0]['GS'] and o[0]['GS']>=20 and o[0]['GP'] and o[0]['GS']/o[0]['GP']>=.8:return 'established'
 if z['role']=='RP' and latest>=40:return 'established'
 return 'unstable'
@functools.lru_cache(None)
def historical_z(ident,year,role):
 rows=hist[ident,'H' if role=='H' else 'P'];return {'id':ident,'year':year,'role':role,'x':base['features'](rows,role,year,ident),'bounded_x':base['features'](rows,role,year,ident,True)}
@functools.lru_cache(None)
def historical_feature(ident,year,role):return evidence_features(historical_z(ident,year,role))
def fz(z):
 x,d=evidence_features(z) if 'history_override' in z else historical_feature(z['id'],z['year'],z['role'])
 if z['role']=='H':
  # GP coverage is current-catalog selected, not a random historical census.
  # Keep status in audit, exclude GP-derived predictors and coverage masks.
  keep=[i for i in range(45) if i not in [15,16,17,18]]+list(range(49,53))+list(range(57,65));x=x[keep]
 return x,d

def fit_model(asof,fam):
 rows=training(asof,calendar=fam=='H',family=fam);rows=[a for a in rows if a['year']<=2025];X=np.stack([fz(a['z'])[0] for a in rows]);w=np.array([a['weight'] for a in rows]);lab=np.array([a['state'] for a in rows]);core=np.array([a['z']['id']%5 in [1,2,3] for a in rows]);calmask=np.array([a['z']['id']%5==4 for a in rows]);y=np.array([a['value'] for a in rows]);groups=np.array([cohort_key(a['z']) for a in rows]);capacity=np.array([fz(a['z'])[1]['healthy_role_capacity'] for a in rows]);depth=np.array([fz(a['z'])[1]['depth'] for a in rows]);model={'family':fam,'asof':asof,'conditional':{},'ratios':{},'calibrators':{}}
 clf=HistGradientBoostingClassifier(**settings).fit(X[core],lab[core],sample_weight=w[core]);model['classifier']=clf
 raw=clf.predict_proba(X);p=np.zeros((len(rows),3))
 for j,c in enumerate(clf.classes_):p[:,int(c)]=raw[:,j]
 for group in ['global','established','interrupted','young','unstable']:
  mask=calmask if group=='global' else calmask&(groups==group);n=int(mask.sum());labels=lab[mask]
  if n>=100 and len(set(labels))==3 and min(np.bincount(labels,minlength=3))>=10:
   model['calibrators'][group]=LogisticRegression(C=1,max_iter=1000).fit(np.log(np.clip(p[mask],1e-6,1)),labels,sample_weight=w[mask])
 for state in [1,2]:
  mask=core&(lab==state)
  if fam=='H':
   model['conditional'][state,'PA']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[mask],y[mask],sample_weight=w[mask]);denom=np.maximum(1,capacity*depth);rat=y/denom
   model['ratios'][state,'PA']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[mask],rat[mask],sample_weight=(w*denom**2)[mask])
  else:
   for key in ['GS','RA']:
    vals=np.array([(a['info'] or {}).get(key,0) for a in rows]);model['conditional'][state,key]=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[mask],vals[mask],sample_weight=w[mask])
    # Normalizing demonstrated rotation GS removes shrinkage across dissimilar capacity scales.
    den=np.maximum(1,capacity) if key=='GS' else np.full(len(rows),60.);ratio=vals/den;model['ratios'][state,key]=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[mask],ratio[mask],sample_weight=(w*den**2)[mask])
 if fam=='H':
  active=core&(lab>0);model['active_mean']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[active],y[active],sample_weight=w[active]);den=np.maximum(1,capacity*depth);model['active_capacity_mean']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[active],(y/den)[active],sample_weight=(w*den**2)[active])
 if fam=='P':
  model['depths']={}
  for kind in ['SP','RP']:
   mask=np.array([bool(a['info'] and a['info']['GP']>0 and (a['info']['GS']==a['info']['GP'] and a['info']['GS']>=3 if kind=='SP' else a['info']['GS']==0)) for a in rows])&core
   vals=np.array([a['raw_value']/a['info']['GP'] if a['info'] and a['info']['GP'] else 0 for a in rows]);weights=w*np.array([min(30,a['info']['GP']) if a['info'] else 0 for a in rows]);reg=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),Ridge(alpha=100));reg.fit(X[mask],vals[mask],ridge__sample_weight=weights[mask]);model['depths'][kind]=reg
 model['manifest']={'asof':asof,'max_target':max(a['year'] for a in rows),'core_mods':[1,2,3],'calibration_mods':[4],'rows':len(rows),'conditional_loss':'squared_error','ratio_weights':'squared capacity: minimizes final count/workload squared error','clinical_labels':False,'feature_count':X.shape[1],'feature_hash':hashlib.sha256(X.tobytes()).hexdigest(),'target_hash':hashlib.sha256(y.tobytes()).hexdigest(),'calibrated_cohorts':list(model['calibrators'])};return model

def probabilities(model,X,zs,variant='supported_cohort_logistic'):
 raw=model['classifier'].predict_proba(X);p=np.zeros((len(X),3))
 for j,c in enumerate(model['classifier'].classes_):p[:,int(c)]=raw[:,j]
 out=p.copy()
 for i,z in enumerate(zs):
  key=cohort_key(z) if variant=='supported_cohort_logistic' else 'global';cal=model['calibrators'].get(key,model['calibrators'].get('global'))
  if cal:
   cp=cal.predict_proba(np.log(np.clip(p[i:i+1],1e-6,1)))[0];out[i]=0
   for j,c in enumerate(cal.classes_):out[i,int(c)]=cp[j]
 return out

def predict_model(model,zs,method='capacity_mean',prob_method='supported_cohort_logistic'):
 fam=model['family'];fs=[fz(z) for z in zs];X=np.stack([a[0] for a in fs]);p=probabilities(model,X,zs,prob_method);cap=np.array([a[1]['healthy_role_capacity'] for a in fs]);depth=np.array([a[1]['depth'] for a in fs]);out=[];statepred={}
 for state in [1,2]:
  for key in ['PA'] if fam=='H' else ['GS','RA']:
   direct=model['conditional'][state,key].predict(X);den=cap*depth if fam=='H' else np.maximum(1,cap) if key=='GS' else np.full(len(zs),60.);ratio=model['ratios'][state,key].predict(X)*den
   # All branches predict conditional means; no median in this mixture.
   ratio=np.where(cap>0,ratio,direct) if key in {'PA','GS'} else ratio
   val=direct if method=='direct_mean' else ratio if method=='capacity_mean' else .5*(direct+ratio)
   statepred[state,key]=np.clip(val,400 if fam=='H' and state==2 else 0,754 if fam=='H' and state==2 else 400 if fam=='H' else 36 if key=='GS' else 85)
 if fam=='H' and method in {'active_mean','active_capacity_mean','active_mean_half','preserved_count_mean','count_mean_75','count_mean_half'}:
  direct=model['active_mean'].predict(X);ratio=model['active_capacity_mean'].predict(X)*cap*depth;ratio=np.where(cap>0,ratio,direct);activepa=np.clip(direct if method=='active_mean' else ratio if method=='active_capacity_mean' else .5*(direct+ratio),0,754)
 if fam=='H' and method in {'preserved_count_mean','count_mean_75','count_mean_half'}:
  LX=np.stack([np.r_[evidence_features(z)[0][:45],fz(z)[1]['depth'],fz(z)[1]['healthy_role_capacity'],np.nan if fz(z)[1]['observations'][0]['GP'] is None else fz(z)[1]['observations'][0]['GP'],fz(z)[1]['observations'][0]['GP'] is None] for z in zs]);countpa=np.clip(model['legacy_count_mean'].predict(LX)*depth,0,754);weight=1 if method=='preserved_count_mean' else .75 if method=='count_mean_75' else .5;activepa=weight*countpa+(1-weight)*np.clip(model['active_mean'].predict(X),0,754)
 if fam=='P':sd=np.clip(model['depths']['SP'].predict(X),2.5,7);rd=np.clip(model['depths']['RP'].predict(X),.25,3)
 for i,z in enumerate(zs):
  q=1-p[i,0];d=fs[i][1];probs={'absent':float(p[i,0]),'part_time' if fam=='H' else 'RP':float(p[i,1]),'regular' if fam=='H' else 'SP':float(p[i,2])}
  if fam=='H':
   cond={str(s):{'PA':float(statepred[s,'PA'][i])} for s in [1,2]};total=sum(p[i,s]*cond[str(s)]['PA'] for s in [1,2]);comp={'PA':float(total),'probabilities':probs,'conditional':cond,'conditional_part_PA':cond['1']['PA'],'conditional_regular_PA':cond['2']['PA'],'conditional_PA':float(total/q) if q else 0}
  else:
   cond={}
   for s in [1,2]:
    gs=float(statepred[s,'GS'][i]);ra=float(min(85-gs,statepred[s,'RA'][i]));ci=gs*float(sd[i])+ra*float(rd[i]);cond[str(s)]={'GS':gs,'RA':ra,'IP':ci,'IP_per_start':float(sd[i]),'IP_per_relief':float(rd[i]),'QA3':0.}
   total=sum(p[i,s]*cond[str(s)]['IP'] for s in [1,2]);comp={'IP':float(total),'GS':float(sum(p[i,s]*cond[str(s)]['GS'] for s in [1,2])),'RA':float(sum(p[i,s]*cond[str(s)]['RA'] for s in [1,2])),'QA3':0.,'probabilities':probs,'conditional':cond,'IP_per_start':float(sd[i]),'IP_per_relief':float(rd[i])}
  if fam=='H' and method in {'active_mean','active_capacity_mean','active_mean_half','preserved_count_mean','count_mean_75','count_mean_half'}:
   expected=float(q*activepa[i]);comp=legacy.reconcile_components(comp,expected,754,'H',method,group=cohort_key(z));comp['conditional']={'1':{'PA':comp['conditional_part_PA']},'2':{'PA':comp['conditional_regular_PA']}};comp['active_mean_before_role_reconciliation']=expected;total=comp['PA']
  comp['opportunity_layer']={'healthy_role_capacity':d['healthy_role_capacity'],'healthy_capacity_kind':d['capacity_status'],'capacity_is_medically_verified':False,'demonstrated_depth':d['depth'],'conditional_active_workload':float(total/q) if q else 0,'participation_probability':float(q),'absence_applied_count':1,'medical_status':'unknown future availability; no numeric penalty','roster_allocation_executed':False,'observation_status':[a['status'] for a in d['observations']],'observations':d['observations'],'method':method,'probability_method':prob_method,'forecast_cohort':cohort_key(z)};out.append(comp)
 return out

def allocate_verified(components,zs,rosters,team_budgets):
 """Execute organization budgets on compatible unconditional expected units.
 Healthy capacity scenarios are NOT summed as if every40-man player were
 simultaneously active. Slot reservation for unmodeled players stays explicit.
 This is a roster membership/budget scenario, not a guaranteed2027 depth chart.
 """
 out=copy.deepcopy(components);ledger=[];groups={}
 for i,(c,z) in enumerate(zip(out,zs)):
  team=rosters.get(z['id']);c['opportunity_layer']['organization_observed']=team
  if team is not None:groups.setdefault((team,z['role']=='H'),[]).append(i)
 for (team,h),indices in groups.items():
  budget=team_budgets.get(team)
  if not budget:continue
  for channel in ['PA'] if h else ['GS','IP']:
   if channel not in budget:continue
   weights=[max(0,float(out[i][channel])) for i in indices];total=sum(weights);limit=float(budget[channel]);scale=min(1,limit/total) if total else 1
   for i,slots in zip(indices,weights):
    c=out[i];layer=c['opportunity_layer'];layer['roster_allocation_executed']=True;layer['roster_asof']='2026-10-10';layer['future_membership_assumption']='verified2026 forty-man membership continues in2027; not guaranteed role';layer.setdefault('allocated_expected_slots',{})[channel]=slots*scale;layer.setdefault('team_budget',{})[channel]=limit;layer['budget_quantity']='unconditional expected PA/GS/IP; absence already included, never reapplied'
    for a in c['conditional'].values():
     if h:a['PA']*=scale
     elif channel=='GS':a['GS']*=scale;a['IP']=a['GS']*a['IP_per_start']+a['RA']*a['IP_per_relief']
     else:a['GS']*=scale;a['RA']*=scale;a['IP']*=scale
    if h:c['PA']*=scale
    elif channel=='GS':c['GS']*=scale;c['IP']=sum(c['probabilities']['RP' if st=='1' else 'SP']*a['IP'] for st,a in c['conditional'].items())
    else:
     for k in ['IP','GS','RA']:c[k]*=scale
   ledger.append({'team_id':team,'channel':channel,'budget':limit,'expected_demand':total,'allocated':total*scale,'unallocated_or_unmodeled_reserve':limit-total*scale,'players':len(indices),'allocation_executed':True,'quantity':'unconditional expected workload','assumption':'current40-man continuation; incomplete future2027 roster'})
 for c,z in zip(out,zs):
  p=c['probabilities'];q=1-p['absent']
  if z['role']=='H':c['conditional_part_PA']=c['conditional']['1']['PA'];c['conditional_regular_PA']=c['conditional']['2']['PA'];c['conditional_PA']=c['PA']/q if q else 0
  c['opportunity_layer']['conditional_active_after_roster']=c['PA' if z['role']=='H' else 'IP']/q if q else 0
 return out,ledger

def apply_verified_availability(component,z,evidence):
 """Explicit, dated forecast-year lost slots only; no generic injury multiplier."""
 c=copy.deepcopy(component);target=z['year']+1
 for e in evidence:
  if e['mlbam_id']!=z['id']:continue
  assert e['published_date']<='2026-10-10' and e['source_url'];c['opportunity_layer'].setdefault('verified_availability_facts',[]).append(e)
  if 'reported_return_window' in e:
   from datetime import date,timedelta
   schedule_path=HERE/'verified'/e['schedule_cache'];assert schedule_path.exists();scheduled=read(schedule_path);dates=[date.fromisoformat(g['officialDate']) for d in scheduled['dates'] for g in d['games'] if g['gameType']=='R'];lo,hi=[date.fromisoformat(t) for t in e['reported_return_window']];assert lo<=hi;grid=[lo+timedelta(days=j) for j in range((hi-lo).days+1)];fraction=float(np.mean([sum(t<return_date for t in dates)/len(dates) for return_date in grid]));lost=c['opportunity_layer']['healthy_role_capacity']*fraction;e=copy.deepcopy(e)|{'expected_missed_appearances':lost,'fact_or_assumption':'explicit_expectation','assumption':'uniform manager-reported recovery window; calendar-proportional capacity envelope, not guaranteed return'};c['opportunity_layer']['medical_capacity_envelope']={'expected_missed_slots':lost,'source_window':e['reported_return_window'],'schedule_games':len(dates),'fraction':fraction,'is_verified_return_date':False}
  if 'expected_missed_appearances' not in e:continue
  assert e['target_year']==target and e['fact_or_assumption']=='explicit_expectation';lost=float(e['expected_missed_appearances']);assert lost>=0
  available=max(0,c['opportunity_layer']['healthy_role_capacity']-lost)
  for a in c['conditional'].values():
   if z['role']=='H':a['PA']=min(a['PA'],available*c['opportunity_layer']['demonstrated_depth'])
   else:a['GS']=min(a['GS'],available);a['IP']=a['GS']*a['IP_per_start']+a['RA']*a['IP_per_relief']
 p=c['probabilities']
 if z['role']=='H':c['PA']=sum(p['part_time' if s=='1' else 'regular']*a['PA'] for s,a in c['conditional'].items());c['conditional_part_PA']=c['conditional']['1']['PA'];c['conditional_regular_PA']=c['conditional']['2']['PA'];c['conditional_PA']=c['PA']/(1-p['absent']) if p['absent']<1 else 0
 else:
  for k in ['IP','GS','RA']:c[k]=sum(p['RP' if s=='1' else 'SP']*a[k] for s,a in c['conditional'].items())
 c['opportunity_layer']['conditional_active_after_availability']=c['PA' if z['role']=='H' else 'IP']/(1-p['absent']) if p['absent']<1 else 0
 return c

class TargetedOpportunityEngine:
 """Callable first-year research adapter. No fitting, deployment or dynasty mutation."""
 def __init__(self,folder=HERE,research_only=False):
  import joblib
  gates=read(Path(folder)/'Release_Gates.json')
  if not research_only and (not gates['all_gates_pass'] or not gates.get('deploy_authorized',False)):raise RuntimeError('Numerical promotion blocked: protected release gates or explicit deployment approval missing. Pass research_only=True for authorized offline experiments.')
  folder=Path(folder);self.selection=read(folder/'Selection_Freeze.json')['selection'];self.models={fam:joblib.load(folder/f'model-{fam}-2026.joblib') for fam in ['H','P']}
 def predict(self,zs,rosters=None,team_budgets=None,availability_evidence=()):
  result=[None]*len(zs)
  for fam in ['H','P']:
   ix=[i for i,z in enumerate(zs) if (z['role']=='H')==(fam=='H')]
   if not ix:continue
   method,prob=self.selection[fam].split('__');ps=predict_model(self.models[fam],[zs[i] for i in ix],method,prob)
   for i,c in zip(ix,ps):result[i]=c
  ledger=[]
  if rosters is not None and team_budgets is not None:result,ledger=allocate_verified(result,zs,rosters,team_budgets)
  result=[apply_verified_availability(c,z,availability_evidence) for c,z in zip(result,zs)]
  return result,ledger

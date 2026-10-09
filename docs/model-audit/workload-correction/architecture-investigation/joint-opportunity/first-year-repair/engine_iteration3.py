"""Research first-year opportunity replacement; no production side effects.
Chronological expert targets already include absence and role attrition. Never
multiply those expected workloads by absence/age a second time.
"""
import sys, hashlib, csv
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import past_only_followup as past
from shared import *
import joblib
from principal_followup import predict_augmented
from hitter_model import predict_hitter
VARIANTS=['appearances','hierarchical','expert_ensemble','joint_ensemble']

def put(name,obj):
 b=json.dumps(obj,allow_nan=False,default=lambda a:a.item() if isinstance(a,np.generic) else a).encode()
 (HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def writecsv(name,rows):
 cols=list(dict.fromkeys(k for a in rows for k in a))
 with (HERE/name).open('w',newline='') as f:w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)

def cohort(z):
 f=z['x'];h=z['role']=='H'
 if f[0]<.6*max(f[1],f[2]) and max(f[1],f[2])>=(400 if h else 100):return 'interrupted'
 if f[13]<=26 and f[14]<=2:return 'young_entry'
 if h:
  if f[11]>=3:return 'durable'
  return 'everyday' if f[0]>=400 else 'part_time'
 if z['role']=='RP':return 'relief_swing'
 return 'stable_rotation' if f[16]>=20 and f[17]>=.8 and f[14]>=3 else 'unstable_rotation'

def fx(z):
 f=past.past_xrow(z,1,z['role']=='H');c=cohort(z)
 # Explicit cohort-specific departures from shared age/workload coefficients.
 indicators=np.array([c==s for s in ['stable_rotation','young_entry','interrupted','unstable_rotation','durable','everyday','part_time']],float)
 xs=np.array([f[0],f[1],f[5],f[6],f[11],f[13]-28,f[14],f[16],f[17],f[21],f[25]],float)
 return np.r_[f,indicators,(indicators[:,None]*xs).ravel()]

def ridgefit(X,y,w):
 reg=make_pipeline(StandardScaler(),Ridge(alpha=250))
 reg.fit(X,y,ridge__sample_weight=w);return reg

def fit(asof,fam):
 rows=[a for a in training(asof,calendar=fam=='H',family=fam) if not a['calibration'] and (fam=='H' or a['z']['role']=='SP')]
 X=np.stack([fx(a['z']) for a in rows]);w=np.array([a['weight'] for a in rows]);y=np.array([a['value'] for a in rows]);labs=np.array([a['state'] for a in rows]);model={'asof':asof,'family':fam,'ridge':ridgefit(X,y,w)}
 # Iteration1: counts learn zero-outcome/role changes, not only surviving starters.
 if fam=='P':
  model['counts']={k:HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X,np.array([a['info'][k] if a['info'] else 0 for a in rows]),sample_weight=w) for k in ['GS','RA']}
 else:
  model['direct']=HistGradientBoostingRegressor(loss='absolute_error',**settings).fit(X,y,sample_weight=w)
 model['cap']=float(max(a['raw_value'] for a in rows if a['year']!=2020))
 model['manifest']={'asof':asof,'latest_target':max(a['year'] for a in rows),'rows':len(rows),'fit_ID_mods':sorted({a['z']['id']%5 for a in rows}),'cohorts':dict(__import__('collections').Counter(cohort(a['z']) for a in rows)),'targets_include_zero_outcomes':True,'ridge_alpha':250,'feature_count':X.shape[1],'feature_hash':hashlib.sha256(X.tobytes()).hexdigest(),'target_hash':hashlib.sha256(y.tobytes()).hexdigest()}
 assert model['manifest']['latest_target']<=asof and model['manifest']['fit_ID_mods']==[1,2,3]
 return model

def incumbent(asof,fam,zs):
 tag='current-'+('hitter' if fam=='H' else 'pitch')+'-one' if asof==2026 else ('hitter' if fam=='H' else 'pitch')+'-'+str(asof)
 model=joblib.load(OUT/('past-'+tag+'.joblib'))
 return predict_hitter(model,zs) if fam=='H' else predict_augmented(model,zs)

def opportunity(model,zs,inc,variant):
 X=np.stack([fx(z) for z in zs]);hier=np.clip(model['ridge'].predict(X),0,model['cap']);fam=model['family'];key='PA' if fam=='H' else 'IP'
 if fam=='H':direct=np.clip(model['direct'].predict(X),0,model['cap']);gs=ra=None
 else:
  gs=np.clip(model['counts']['GS'].predict(X),0,36);ra=np.clip(model['counts']['RA'].predict(X),0,85)
  direct=np.array([a*c['IP_per_start']+b*c['IP_per_relief'] for a,b,c in zip(gs,ra,inc)])
 target=direct if variant=='appearances' else hier if variant=='hierarchical' else .5*(direct+hier) if variant=='expert_ensemble' else .5*(hier+np.array([c[key] for c in inc]))
 results=[]
 for i,(z,c,t) in enumerate(zip(zs,inc,target)):
  if fam=='P' and z['role']=='RP':results.append(copy.deepcopy(c));continue
  results.append(reconcile_components(c,float(t),model['cap'],fam,variant,gs[i] if gs is not None else None,ra[i] if ra is not None else None,cohort(z)))
 return results

def reconcile_components(c,total,cap,fam,variant,gs=None,ra=None,group=None):
 q=copy.deepcopy(c);q['opportunity_architecture']=variant;q['forecast_cohort']=group;q['expert_unconstrained_workload']=total;q['workload_has_absence_included']=True
 if fam=='H':
  p=q['probabilities'];active=1-p['absent'];desired=min(cap*active,max(0,total));part=q['conditional_part_PA'];reg=q['conditional_regular_PA']
  # Constrained mixture mean: replace incoherent separate active-hurdle forecast.
  # Find a common opportunity shift, retaining role conditional interval bounds.
  lo=-cap;hi=cap
  for _ in range(60):
   d=(lo+hi)/2;a=np.clip(part+d,0,400);b=np.clip(reg+d,400,cap);value=p['part_time']*a+p['regular']*b
   if value<desired:lo=d
   else:hi=d
  d=(lo+hi)/2;part=float(np.clip(part+d,0,400));reg=float(np.clip(reg+d,400,cap))
  q['conditional_part_PA']=part;q['conditional_regular_PA']=reg;q['PA']=p['part_time']*part+p['regular']*reg;q['conditional_PA']=q['PA']/active if active else 0
  q['mixture_constraint_residual']=q['PA']-total
  return q
 # Forecast total already includes attrition. Conditional components are a
 # constrained allocation for audit, not another probability discount.
 p=q['probabilities'];states=q['conditional'];initial=sum(p['RP' if s=='1' else 'SP']*a['IP'] for s,a in states.items())
 factor=max(0,total)/initial if initial else 0
 for s,a in states.items():
  a['GS']=min(36,a['GS']*factor);a['RA']=min(85-a['GS'],a['RA']*factor)
  depth=a['IP_per_start'];relief=a['IP_per_relief'];a['IP']=a['GS']*depth+a['RA']*relief
  # Principal-state QA3 rate preserved, rescaled by appearances and bounded.
  a['QA3']=min(a['IP']/5,a['GS']+a['RA'],a['QA3']*factor)
 for key in ['IP','GS','RA','QA3']:q[key]=sum(p['RP' if s=='1' else 'SP']*a[key] for s,a in states.items())
 q['unconditional_start_expert']=float(gs);q['unconditional_relief_expert']=float(ra);q['mixture_constraint_residual']=q['IP']-total
 return q

def stats(b,c,rr):
 key='PA' if rr=='H' else 'IP';ratio=c[key]/b[key] if b[key]>0 else 0;s={k:val*ratio for k,val in b.items()}
 if rr=='H':return v.reconcile(s)
 s['QA3']=c['QA3'];s['GS']=c['GS'];s['RA']=c['RA']
 for k in ['SV','HLD']:s[k]=b.get(k,0)*min(1,ratio)
 return s

def assert_coherent(c,s,rr,cap):
 p=c['probabilities'];assert abs(sum(p.values())-1)<1e-8 and min(p.values())>=0
 assert all(math.isfinite(a) and a>=-1e-7 for a in s.values())
 if rr=='H':
  assert s['HR']<=s['H']+1e-7 and s['H']<=s['AB']+1e-7 and s['AB']<=s['PA']+1e-7
  assert s['AB']+s['BB']+s['HBP']+s['SF']<=s['PA']+1e-7
  assert s['H']+3*s['HR']<=s['TB']+1e-7 and s['TB']<=4*s['H']+1e-7
  assert c['conditional_regular_PA']<=cap+1e-7
  expected=p['part_time']*c['conditional_part_PA']+p['regular']*c['conditional_regular_PA'];assert abs(expected-s['PA'])<1e-7
 else:
  assert s['QA3']<=s['IP']/5+1e-7
  for a in c['conditional'].values():assert a['GS']<=36+1e-7 and a['GS']+a['RA']<=85+1e-7
  assert abs(sum(p['RP' if k=='1' else 'SP']*a['IP'] for k,a in c['conditional'].items())-s['IP'])<1e-7

class FirstYearForecastEngine:
 """Callable research adapter. Load frozen selection and fitted model files."""
 def __init__(self,artifact_dir=HERE):
  folder=Path(artifact_dir);self.selection=json.loads((folder/'Selection_Freeze.json').read_text())['selected'];self.models={fam:joblib.load(folder/f'current-{fam}.joblib') for fam in ['P','H']}
 def predict(self,zs):
  result=[]
  for z in zs:
   fam='H' if z['role']=='H' else 'P';c=incumbent(2026,fam,[z]);variant=self.selection[fam]
   result.extend(c if variant=='incumbent' else opportunity(self.models[fam],[z],c,variant))
  return result

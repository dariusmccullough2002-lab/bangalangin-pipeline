"""Own role/opportunity forecasts. Public forecasts are evaluation-only.
Separate per-appearance depth, role/opportunity counts, and probability of MLB
participation. Missing medical evidence is never interpreted as health.
"""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'first-year-repair'))
import importlib.util
_spec=importlib.util.spec_from_file_location("prior_repair_engine",HERE.parent/"first-year-repair"/"engine.py")
prior=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(prior)
globals().update({k:val for k,val in vars(prior).items() if not k.startswith("_")})
HERE=Path(__file__).resolve().parent
GP={}
for p in json.loads(Path(sys.argv[1]+'/trade-preview-v22/model/career_history_cache.json').read_text())['profiles']:
 for a in p.get('seasons',[]):
  if a['role']=='H':
   n=a.get('skills',{}).get('gamesPlayed',a.get('stat',{}).get('GP'))
   if n is not None:GP[a['id'],a['year']]=float(n)

def observed(z):
 h=z['role']=='H';rows=z.get('history_override',hist.get((z['id'],'H' if h else 'P'),[]));by={a['year']:a for a in rows if a['year']<=z['year']};out=[]
 for yr in range(z['year'],z['year']-3,-1):
  a=by.get(yr);s=a['stat'] if a else {};ex=s.get('PA' if h else 'IP',0)
  info=counts(z['id'],yr) if not h else None
  gp=GP.get((z['id'],yr)) if h else ((info or {}).get('GP'))
  gs=None if h else ((info or {}).get('GS'))
  if yr==2026 and not h:gp=float(z['x'][15]);gs=float(z['x'][16])
  fac=162/60 if yr==2020 else 1
  out.append({'ex':ex*fac,'gp':None if gp is None else gp*fac,'gs':None if gs is None else gs*fac})
 return out

def decomposition(z):
 h=z['role']=='H';o=observed(z);weights=[3,2,1];good=[(a,w) for a,w in zip(o,weights) if a['gp'] and a['ex']>0]
 if h:
  depth=(sum(a['ex']*w for a,w in good)+20*4.1)/(sum(a['gp']*w for a,w in good)+20) if good else 4.1
  opportunity=max([a['gp'] for a in o if a['gp'] is not None],default=z['x'][0]/depth)
  opportunity=min(162,opportunity);latest=o[0]['gp'];missing=latest is None
 else:
  starters=[(a,w) for a,w in good if a['gs'] and a['gs']/a['gp']>=.8]
  depth=(sum(a['ex']*w for a,w in starters)+5*5.5)/(sum(a['gs']*w for a,w in starters)+5) if starters else 5.5
  opportunity=min(34,max([a['gs'] or 0 for a in o],default=0));latest=o[0]['gs'];missing=latest is None
 return {'depth':float(np.clip(depth,2 if h else 2.5,5.2 if h else 7)), 'healthy_opportunity':float(opportunity),'latest_opportunity':float(latest or 0),'counts_missing':missing,'observations':o}

def features(z):
 d=decomposition(z);return np.r_[past.past_xrow(z,1,z['role']=='H'),d['depth'],d['healthy_opportunity'],d['latest_opportunity'],d['counts_missing']]

def fit_layer(asof,fam):
 rows=[a for a in training(asof,calendar=fam=='H',family=fam) if not a['calibration'] and (fam=='H' or a['z']['role']=='SP')]
 use=[]
 for a in rows:
  if fam=='H':cnt=a['raw_value']/decomposition(a['z'])['depth']
  else:cnt=(a['info'] or {}).get('GS',0)
  if cnt is not None:use.append((a,cnt*a['factor']))
 X=np.stack([features(a['z']) for a,c in use]);y=np.array([c for a,c in use]);w=np.array([a['weight'] for a,c in use]);active=np.array([a['value']>0 for a,c in use]);out={'asof':asof,'family':fam,'fits':{}}
 for alpha in [100,1000,10000]:
  reg=make_pipeline(StandardScaler(),Ridge(alpha=alpha));reg.fit(X[active],y[active],ridge__sample_weight=w[active]);out['fits'][str(alpha)]=reg
 out['tree']=HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X[active],y[active],sample_weight=w[active])
 # Transparent own usage baseline: completed, disjoint-core empirical expected
 # future count / healthy recent count, shrunken within usage and age bands.
 buckets={}
 for a,c in use:
  d=decomposition(a['z']);k=bucket(a['z']);buckets.setdefault(k,[]).append((c,d['healthy_opportunity']))
 globalratio=sum(c for a,c in use)/max(1,sum(decomposition(a['z'])['healthy_opportunity'] for a,c in use))
 out['retention']={k:(sum(c for c,n in xs)+30*globalratio)/(sum(n for c,n in xs)+30) for k,xs in buckets.items()};out['global_retention']=globalratio
 out['manifest']={'asof':asof,'target_end':max(a['year'] for a,c in use),'core_ID_mods':sorted({a['z']['id']%5 for a,c in use}),'count_rows':len(use),'excluded_missing_count_rows':len(rows)-len(use),'count_target_hash':hashlib.sha256(y.tobytes()).hexdigest(),'medical_cause_labels':False,'H_count_target':'future PA / as-of smoothed PA-per-game; appearance equivalents, not future observed games'}
 return out

def bucket(z):
 d=decomposition(z);threshold=120 if z['role']=='H' else 24
 return str(int(d['healthy_opportunity']>=threshold))+':'+str(int(z['x'][13]>=33))

def predict_layer(model,zs,inc,variant):
 if variant in {'tree_quarter','tree_half','ridge_quarter','usage_quarter'}:
  method='tree' if variant.startswith('tree') else 'ridge_100' if variant.startswith('ridge') else 'usage';weight=.5 if variant.endswith('half') else .25
  fresh=predict_layer(model,zs,inc,method);result=[]
  for z,c,q in zip(zs,inc,fresh):
   key='PA' if z['role']=='H' else 'IP';total=(1-weight)*c[key]+weight*q[key]
   mixed=reconcile_components(c,total,754 if key=='PA' else 251,'H' if key=='PA' else 'P',variant,q.get('GS',0),q.get('RA',0),cohort(z));mixed['opportunity_layer']=q['opportunity_layer']|{'weight':weight,'incumbent_weight':1-weight};result.append(mixed)
  return result
 h=model['family']=='H';X=np.stack([features(z) for z in zs]);alpha=variant.replace('ridge_','');cap=162 if h else 34
 if variant.startswith('ridge_'):activecounts=np.clip(model['fits'][alpha].predict(X),0,cap)
 elif variant=='tree':activecounts=np.clip(model['tree'].predict(X),0,cap)
 else:activecounts=None
 out=[]
 for i,(z,c) in enumerate(zip(zs,inc)):
  d=decomposition(z);basecount=np.clip(d['healthy_opportunity']*model['retention'].get(bucket(z),model['global_retention']),0,cap)
  active=1-c['probabilities']['absent']
  count=basecount if variant=='usage' else (.5*basecount+.5*float(np.clip(model['fits']['1000'].predict(X[i:i+1])[0],0,cap))*active if variant=='blend' else activecounts[i]*active)
  # Usage baseline already includes zero outcomes; never apply absence again.
  expected=count*d['depth']
  if not h:expected+=c.get('RA',0)*c.get('IP_per_relief',1)
  q=reconcile_components(c,float(expected),754 if h else 251,'H' if h else 'P',variant,float(count),float(c.get('RA',0)),cohort(z))
  q['opportunity_layer']={'expected_appearances':float(count),'healthy_role_appearances':d['healthy_opportunity'],'work_per_appearance':d['depth'],'MLB_participation_probability':active,'medical_availability':'unknown','roster_depth':'not supplied','role_evidence':'demonstrated MLB usage','counts_missing':d['counts_missing'],'zero_outcomes_included_once':True}
  out.append(q)
 return out

class EvidenceContract:
 """Dated factual inputs; no current roster backfill into historical anchors."""
 @staticmethod
 def validate(evidence,asof,target_year):
  from datetime import date
  end=date.fromisoformat(asof)
  for e in evidence:
   assert e['source_url'] and e['evidence_kind'] in {'roster','injury','team_usage'}
   assert date.fromisoformat(e['published_date'])<=end
   assert e['target_year']==target_year
   assert e['fact_or_assumption'] in {'verified_fact','explicit_expectation'}
  return evidence
 @staticmethod
 def allocate_team(rows,total):
  # Normalize healthy-role slots before player-specific availability. Team
  # budget is never a player minimum and no missing roster is invented.
  assert total>=0 and all(a['healthy_slots']>=0 for a in rows)
  allocated=np.zeros(len(rows));remaining=float(total);active={i for i,a in enumerate(rows) if a['healthy_slots']>0}
  while active and remaining>1e-9:
   mass=sum(rows[i]['healthy_slots'] for i in active);capped=[];proposal={i:remaining*rows[i]['healthy_slots']/mass for i in active}
   for i in active:
    room=max(0,rows[i].get('max_slots',float('inf'))-allocated[i])
    if proposal[i]>=room:capped.append((i,room))
   if not capped:
    for i,value in proposal.items():allocated[i]+=value
    remaining=0;break
   for i,room in capped:allocated[i]+=room;remaining-=room;active.remove(i)
  return [a|{'allocated_slots':float(allocated[i]),'team_unallocated_slots':remaining} for i,a in enumerate(rows)]

def apply_evidence(component,z,evidence,asof):
 """Optional factual opportunity overrides; no forecast source substitution.
 Healthy appearances require a dated team allocation. Verified injuries carry
 no numerical penalty without a separately labeled expected missed count.
 """
 EvidenceContract.validate(evidence,asof,z['year']+1);q=copy.deepcopy(component);layer=q.setdefault('opportunity_layer',{});d=decomposition(z);count=q['PA' if z['role']=='H' else 'IP']/d['depth'];active=1-q['probabilities']['absent'];applied=[]
 for e in evidence:
  if e.get('mlbam_id')!=z['id']:continue
  if e['evidence_kind']=='roster':layer['roster_role_evidence']=e.get('status','dated roster observation')
  if e['evidence_kind']=='roster' and 'allocated_healthy_appearances' in e:
   assert e['fact_or_assumption']=='explicit_expectation' and e.get('team_budget_id')
   count=float(e['allocated_healthy_appearances'])*active;applied.append(e)
  if e['evidence_kind']=='injury':
   layer['verified_injury_status']=e.get('status','documented injury');layer['injury_evidence']='verified current fact; forecast-year timetable missing';applied.append(e)
   if 'expected_unavailable_appearances' in e:
    assert e['fact_or_assumption']=='explicit_expectation';assert e['expected_unavailable_appearances']>=0
    # Cap opportunity to medically available slots, never re-discount expected
    # statistical work by a second generic absence probability.
    count=min(count,max(0,d['healthy_opportunity']-e['expected_unavailable_appearances'])*active)
 total=count*d['depth'];out=reconcile_components(q,total,754 if z['role']=='H' else 251,'H' if z['role']=='H' else 'P','dated_evidence',count,q.get('RA',0),cohort(z));out['opportunity_layer']=layer|{'applied_evidence':applied,'expected_appearances':count};return out

class RoleOpportunityEngine:
 def __init__(self,folder=HERE):
  self.folder=Path(folder);self.selection=read(self.folder/'Selection_Freeze.json')['selected'];self.models={f:joblib.load(self.folder/f'current-{f}.joblib') for f in ['P','H']}
 def predict(self,zs,evidence=(),asof='2026-10-09'):
  out=[]
  for z in zs:
   fam='H' if z['role']=='H' else 'P';c=incumbent(2026,fam,[z])[0];method=self.selection[fam]
   q=c if z['role']=='RP' or method=='incumbent' else predict_layer(self.models[fam],[z],[c],method)[0]
   if any(e.get('mlbam_id')==z['id'] for e in evidence):q=apply_evidence(q,z,evidence,asof)
   out.append(q)
  return out

@functools.lru_cache(None)
def _incmodel(asof,fam):
 tag='current-'+('hitter' if fam=='H' else 'pitch')+'-one' if asof==2026 else ('hitter' if fam=='H' else 'pitch')+'-'+str(asof)
 return joblib.load(OUT/('past-'+tag+'.joblib'))
def incumbent(asof,fam,zs):
 model=_incmodel(asof,fam)
 return predict_hitter(model,zs) if fam=='H' else predict_augmented(model,zs)

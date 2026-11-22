"""Contact versus damage: frozen cohort study and broad descriptive display.
Requires numpy/scikit-learn. Inputs are cached public TJ leaderboard responses
and MLB people identities; neither future outcomes nor debut dates are features.
"""
from pathlib import Path
import json,gzip,hashlib,math,os,urllib.request,concurrent.futures
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss,brier_score_loss
ROOT=Path(__file__).resolve().parents[1];CACHE=Path(os.environ.get('POWER_SOURCE_CACHE',ROOT.parent/'prospect-source-cache'));OUT=ROOT/'data/research';ASOF='2026-11-21'
LEVELS=['lo-a','hi-a','aa','aaa'];ORDER={x:i for i,x in enumerate(LEVELS)};SOURCES=[];AUDIT=[]
def ensure_sources():
 CACHE.mkdir(exist_ok=True)
 tasks=[(y,l) for y in range(2021,2027) for l in (LEVELS+(['rok'] if y>=2024 else []))]+[(y,'mlb') for y in range(2021,2027)]
 def get(t):
  y,l=t;p=CACHE/f'tj-{y}-{l}.json'
  if not p.exists():
   u=f'https://tjstats.ca/?tjs_data=leaderboard&role=batter&season={y}&game_type=R&level={l}&min_pa=1&limit=10000'
   raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read();assert json.loads(raw)['success'];p.write_bytes(raw)
 with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(get,tasks))
 ids=set()
 for y in [2021,2022,2023]:
  for l in LEVELS:
   for r in json.loads((CACHE/f'tj-{y}-{l}.json').read_text())['data']['players']:
    if r['pa']>=150 and r.get('age') is not None and 16<=r['age']<=26:ids.add(int(r['player_id']))
 ids=sorted(ids)
 for i in range(0,len(ids),100):
  p=CACHE/f'contact-people-{i//100}.json';batch=set(ids[i:i+100]);u='https://statsapi.mlb.com/api/v1/people?personIds='+','.join(map(str,sorted(batch)))+'&fields=people,id,mlbDebutDate,birthDate'
  if not p.exists() or {r['id'] for r in json.loads(p.read_text())['people']}!=batch:p.write_bytes(urllib.request.urlopen(u,timeout=60).read())
 return set(ids)
def read(y,l):
 p=CACHE/f'tj-{y}-{l}.json';raw=p.read_bytes();d=json.loads(raw);assert d['success'];rows=d['data']['players'];assert d['data']['count']==len(rows)
 SOURCES.append(dict(file=p.name,url=f'https://tjstats.ca/?tjs_data=leaderboard&role=batter&season={y}&game_type=R&level={l}&min_pa=1&limit=10000',sha256=hashlib.sha256(raw).hexdigest(),retrieved=ASOF if y<2024 or l=='mlb' else '2026-11-20',rows=len(rows)))
 groups={}
 for r in rows:groups.setdefault(int(r['player_id']),[]).append(r)
 clean=[]
 for pid,group in groups.items():
  if len({json.dumps(r,sort_keys=True) for r in group})>1:AUDIT.append(dict(year=y,level=l,id=pid,reason='conflicting provider rows'));continue
  clean.append(group[0])
 return clean

def fields(r):
 return dict(whiff=100*r['whiff_rate'] if r.get('whiff_rate') is not None else None,iso=r.get('iso'),pullAir=100*r['pulled_air_percent'] if r.get('pulled_air_percent') is not None else None,k=100*r['k_percent'] if r.get('k_percent') is not None else None,bb=100*r['bb_percent'] if r.get('bb_percent') is not None else None,age=r.get('age'),logPA=math.log(max(r['pa'],1)),level=r['level'])
def vector(r,names):
 f=fields(r) if 'player_id' in r else r
 return [int(f['level']==n[6:]) if n.startswith('level:') else f[n] for n in names]
def metrics(y,p):
 return dict(n=len(y),events=int(sum(y)),eventRate=float(np.mean(y)),auc=float(roc_auc_score(y,p)) if len(set(y))==2 else None,averagePrecision=float(average_precision_score(y,p)) if sum(y)>0 else None,logLoss=float(log_loss(y,p,labels=[0,1])),brier=float(brier_score_loss(y,p)))
def fit(rows,names,C):
 x=np.array([vector(r,names) for r in rows]);mu=x.mean(0);sd=x.std(0);sd[sd==0]=1
 m=LogisticRegression(C=C,max_iter=3000).fit((x-mu)/sd,[r['outcome'] for r in rows]);return m,mu,sd

def predict(model,rows,names):
 m,mu,sd=model;return m.predict_proba((np.array([vector(r,names) for r in rows])-mu)/sd)[:,1]
def main():
 expected_ids=ensure_sources();people={}
 for p in sorted(CACHE.glob('contact-people-*.json')):
  raw=p.read_bytes();SOURCES.append(dict(file=p.name,sha256=hashlib.sha256(raw).hexdigest(),provider='MLB Stats API people',retrieved=ASOF));people.update({r['id']:r for r in json.loads(raw)['people'] if r['id'] in expected_ids})
 assert set(people)==expected_ids
 mlb={y:read(y,'mlb') for y in range(2021,2027)};mlbIndex={y:{r['player_id']:r for r in rows} for y,rows in mlb.items()}
 allrows=[r for y in [2021,2022,2023] for l in LEVELS for r in read(y,l)];candidates={};exclusions={'missingIdentity':0,'previousMLBDebut':0,'unresolvedFollowup':0}
 for r in allrows:
  if r['pa']<150 or r.get('bip',0)<50 or r.get('age') is None or not 16<=r['age']<=26 or any(r.get(k) is None for k in ['whiff_rate','iso','k_percent','bb_percent']):continue
  pid=r['player_id'];person=people.get(pid)
  if not person:exclusions['missingIdentity']+=1;continue
  debut=person.get('mlbDebutDate')
  if debut and int(debut[:4])<=r['season']:exclusions['previousMLBDebut']+=1;continue
  candidates.setdefault(pid,[]).append(r)
 cohorts=[]
 for pid,rs in candidates.items():
  year=min(r['season'] for r in rs);r=max([r for r in rs if r['season']==year],key=lambda r:(ORDER[r['level']],r['pa']));future=[mlbIndex[y].get(pid) for y in [year+1,year+2]]
  event=any(x and x['pa']>=250 and x.get('iso') is not None and x.get('woba_percent') is not None and x['iso']>=.200 and x['woba_percent']>=.330 for x in future)
  debut=people[pid].get('mlbDebutDate');unresolved=not event and ((debut and year<int(debut[:4])<=year+2 and not any(future)) or any(x and (x.get('iso') is None or x.get('woba_percent') is None) for x in future) or any(a['id']==pid and a['level']=='mlb' and a['year'] in [year+1,year+2] for a in AUDIT))
  if unresolved:exclusions['unresolvedFollowup']+=1;continue
  cohorts.append(dict(r,outcome=int(event),followupYears=[year+1,year+2]))
 train=[r for r in cohorts if r['season']==2021];val=[r for r in cohorts if r['season']==2022];test=[r for r in cohorts if r['season']==2023];dev=train+val
 print('COHORTS',[(yr,len([r for r in cohorts if r['season']==yr]),sum(r['outcome'] for r in cohorts if r['season']==yr)) for yr in [2021,2022,2023]],flush=True)
 context=['age','logPA','level:hi-a','level:aa','level:aaa']
 specs={'Context only':context,'ISO + context':['iso']+context,'Whiff + ISO':['whiff','iso']+context,'Whiff + ISO + K + BB':['whiff','iso','k','bb']+context}
 results=[];models={}
 for name,names in specs.items():
  trials=[]
  for C in [.1,1,10]:
   model=fit(train,names,C);trials.append((metrics([r['outcome'] for r in val],predict(model,val,names))['logLoss'],C))
  loss,C=min(trials);models[name]=fit(dev,names,C);p=predict(models[name],test,names)
  results.append(dict(name=name,features=names,C=C,validationLogLoss=loss,test=metrics([r['outcome'] for r in test],p)))
 # Selection uses validation only, and retains an interpretable two-axis view.
 selected=min(results,key=lambda r:r['validationLogLoss']);names=selected['features'];model=models[selected['name']];m,mu,sd=model
 rng=np.random.default_rng(20261121);y=np.array([r['outcome'] for r in test]);pred=predict(model,test,names);base=predict(models['ISO + context'],test,specs['ISO + context']);diff=[]
 for _ in range(1000):
  ix=rng.integers(0,len(test),len(test))
  if len(set(y[ix]))==2:diff.append(roc_auc_score(y[ix],pred[ix])-roc_auc_score(y[ix],base[ix]))
 current=[]
 for year in [2024,2025,2026]:
  for level in LEVELS+['rok']:
   for r in read(year,level):
    f=fields(r);current.append(dict(id=f"cd-tj-{r['player_id']}-{year}-{level}",mlbamId=int(r['player_id']),name=r['player_name'],year=year,pa=r['pa'],bip=r.get('bip'),source='TJ Stats',sourceUrl=f'https://tjstats.ca/leaderboard/?role=batter&season={year}&game_type=R&level={level}&min_pa=1&group_by=player',**f))
 # Keep PS DSL/complex and source alternatives searchable, without imputing.
 panel=json.loads(gzip.decompress((OUT/'power-prospect-records.json.gz').read_bytes()))
 for r in panel['records']:
  if r['source']=='TJ Stats':continue
  level={'AAA':'aaa','AA':'aa','High-A':'hi-a','FSL A':'lo-a','A (Carolina / California)':'lo-a','DSL (Rookie)':'rok','Complex (Rookie)':'rok'}.get(r['level'])
  if not level:continue
  current.append(dict(id='cd-'+r['id'],mlbamId=r['mlbamId'],name=r['name'],year=r['year'],pa=r['pa'],bip=r.get('trackedBBE'),source=r['source'],sourceUrl=r['sourceUrl'],whiff=r['whiff'],iso=r['iso'],pullAir=r.get('pullAir'),k=r.get('k'),bb=r.get('bb'),age=r.get('seasonAge'),logPA=math.log(max(r['pa'],1)),level=level,environment=r['level']))
 landmarks=[592450,660271,621566,665742,656941,547180,571970,665833,694022]
 benchmarks=[r for r in mlb[2025] if r['pa']>=250 and r.get('whiff_rate') is not None and r.get('iso') is not None];benchmarks.sort(key=lambda r:r['whiff_rate']);points=[]
 for pid in landmarks:
  match=next((r for r in benchmarks if r['player_id']==pid),None)
  if match:points.append(match)
 for i in np.linspace(0,len(benchmarks)-1,25-len(points),dtype=int):
  r=benchmarks[i]
  if r['player_id'] not in {p['player_id'] for p in points}:points.append(r)
 for r in benchmarks:
  if len(points)>=25:break
  if r['player_id'] not in {p['player_id'] for p in points}:points.append(r)
 refs=[dict(id='mlb-'+str(r['player_id']),mlbamId=r['player_id'],name=r['player_name'],year=2025,pa=r['pa'],**fields(dict(r,level='mlb'))) for r in points]
 study=dict(asOf=ASOF,title='Contact versus damage — retrospective cohort audit',endpoint='Within the next two seasons, at least one MLB season with 250+ PA, ISO ≥ .200 and TJ wOBA ≥ .330. Non-attainment within this window is not career failure.',selection='One record per player: earliest eligible season in 2021–2023, then highest level with 150+ PA and 50+ provider BIP, age 16–26. No MLB debut by the end of the index year. All model candidates use the same complete-case cohort.',split=dict(trainYear=2021,validationYear=2022,testYear=2023,followupThrough=2025),cohorts={str(y):dict(n=sum(r['season']==y for r in cohorts),events=sum(r['outcome'] for r in cohorts if r['season']==y)) for y in [2021,2022,2023]},results=results,selected=selected['name'],aucDifferenceVsISO=dict(estimate=float(roc_auc_score(y,pred)-roc_auc_score(y,base)) if len(set(y))==2 else None,interval95=list(map(float,np.quantile(diff,[.025,.975]))) if diff else None),model=dict(features=names,means=mu.tolist(),scales=sd.tolist(),coefficients=m.coef_[0].tolist(),intercept=float(m.intercept_[0]),referenceRate=float(np.mean([r['outcome'] for r in dev])),reference={k:float(np.mean([fields(r)[k] for r in dev if fields(r)[k] is not None])) if any(fields(r)[k] is not None for r in dev) else None for k in ['whiff','iso','pullAir','k','bb','age','logPA']},ranges={k:[float(np.min([fields(r)[k] for r in dev if fields(r)[k] is not None])) if any(fields(r)[k] is not None for r in dev) else None,float(np.max([fields(r)[k] for r in dev if fields(r)[k] is not None])) if any(fields(r)[k] is not None for r in dev) else None] for k in ['whiff','iso','pullAir','k','bb','age','logPA']}),exclusions=exclusions,sourceConflicts=AUDIT,sources=SOURCES,limits=['Pulled-air data is sparse in the historical training years. It is shown descriptively but excluded from the fitted candidates; no missing values are imputed.','Historical snapshots were retrieved retrospectively, not frozen at the original season end.','Earliest eligible season in this window is not necessarily the first professional season; 2021 COVID-era context may shift relationships.','Predicts a combined MLB opportunity and performance endpoint within two years, not pure hitting talent or career ceiling.','No park or league-specific adjustment; level, age and source PA are context features only.','Validation selects candidates; the 2023 test was not used for selection, but is now inspected and requires new independent confirmation.','The player-disjoint 2023 cohort has zero observed endpoint events within two years: test AUC and AUC improvement cannot be estimated. This fitted model is not a validated forecasting tool.','Training/validation outcome windows overlap calendar years; disjoint player IDs prevent direct reuse but this is a retrospective cohort comparison, not a strict as-of deployment backtest.','No inferred Hard-Hit or Barrel rates. No individual prospect probability or ranking is published.','Rookie/DSL/complex are outside the fitted level range. Their points are descriptive only.','The meridian holds context fixed and marks the training cohort event-rate reference, not a 50% boundary or a pass/fail threshold.'])
 for key,value in [('contact-damage-study',study),('contact-damage-records',dict(asOf=ASOF,records=current,benchmarks=refs))]:
  raw=json.dumps(value,separators=(',',':'),allow_nan=False).encode();(OUT/(key+'.json.gz')).write_bytes(gzip.compress(raw,mtime=0))
 audit=[dict(mlbamId=r['player_id'],name=r['player_name'],year=r['season'],pa=r['pa'],outcome=r['outcome'],followupYears=r['followupYears'],**fields(r)) for r in cohorts]
 (OUT/'contact-damage-cohort.json.gz').write_bytes(gzip.compress(json.dumps(audit,separators=(',',':')).encode(),mtime=0))
 print(json.dumps(dict(cohorts=study['cohorts'],selected=study['selected'],results=results,comparison=study['aucDifferenceVsISO'],records=len(current)),indent=2))
if __name__=='__main__':main()

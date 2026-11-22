"""DEVERS V1: same-season MLB research + relative prospect profile index.
No invented measurements, MLB-equivalence claims, or individual probabilities.
"""
from pathlib import Path
import json,gzip,hashlib,math,importlib.util,os,urllib.request,urllib.parse,concurrent.futures
from collections import Counter,defaultdict
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge,LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error,r2_score,roc_auc_score,log_loss
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research';CACHE=Path(os.environ.get('POWER_SOURCE_CACHE',ROOT.parent/'prospect-source-cache'));DATE='2026-11-21';SOURCES=[]
def dump(name,data):
 (OUT/(name+'.json.gz')).write_bytes(gzip.compress(json.dumps(data,separators=(',',':'),allow_nan=False).encode(),mtime=0))
def readcache(file):
 raw=(CACHE/file).read_bytes();SOURCES.append(dict(file=file,sha256=hashlib.sha256(raw).hexdigest()));return json.loads(raw)
def quantile(sorted_values,p):return float(np.quantile(sorted_values,p,method='linear'))
def pctile(values,x):
 v=np.asarray(values);return float(((v<x).sum()+.5*(v==x).sum())/len(v))
def predict_fit(rows,features,target,alpha):
 return make_pipeline(StandardScaler(),Ridge(alpha=alpha)).fit([[r[k] for k in features] for r in rows],[r[target] for r in rows])
def proxy_metrics(rows,p,target):
 actual=np.array([r[target] for r in rows]);rho=spearmanr(actual,p).statistic;order=np.argsort(p);bins=[]
 for ids in np.array_split(order,10):
  if len(ids):bins.append(dict(n=len(ids),predicted=float(np.mean(np.array(p)[ids])),observed=float(np.mean(actual[ids]))))
 return dict(n=len(rows),r2=float(r2_score(actual,p)),mae=float(mean_absolute_error(actual,p)),rankCorrelation=float(rho),percentileCalibration=bins)
def fit_survival(rows,features,C):
 return make_pipeline(StandardScaler(),LogisticRegression(C=C,max_iter=3000)).fit([[r[k] for k in features] for r in rows],[r['endpoint'] for r in rows])
def export_model(pipe,rows,features):
 scale,fit=pipe.steps[0][1],pipe.steps[1][1];co=fit.coef_[0]/scale.scale_;inter=float(fit.intercept_[0]-co@scale.mean_);margins=np.array([[r[k] for k in features] for r in rows])@co+inter
 return dict(features=features,coefficients=co.tolist(),intercept=inter,means=scale.mean_.tolist(),scales=scale.scale_.tolist(),marginScale=float(np.std(margins)),reference={k:sorted(float(r[k]) for r in rows) for k in features})
def ensure_cache():
 CACHE.mkdir(exist_ok=True);tasks=[]
 for y in range(2021,2027):
  tasks.extend([(f'tj-{y}-mlb.json',f'https://tjstats.ca/?tjs_data=leaderboard&role=batter&season={y}&game_type=R&level=mlb&min_pa=1&limit=10000'),(f'devers-mlb-counts-{y}.json',f'https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={y}&sportIds=1&limit=10000&playerPool=ALL')])
 for y in [2024,2025,2026]:
  for l in ['AAA','AA','High-A','A','Rk']:
   code='A+' if l=='High-A' else l;tasks.append((f'ps-{y}-{l}.json',f'https://oriolebird.pythonanywhere.com/leaders/hitters/{urllib.parse.quote(code,safe="")}/{y}/1/0/99'))
 def fetch(t):
  file,url=t;p=CACHE/file
  if not p.exists():
   raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read();json.loads(raw);p.write_bytes(raw)
 with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(fetch,tasks))
 panel=json.loads(gzip.decompress((OUT/'power-prospect-records.json.gz').read_bytes()));ids=sorted({r['mlbamId'] for r in panel['records'] if r['pa']>=100});tasks=[]
 for i in range(0,len(ids),100):
  b=ids[i:i+100];tasks.append((f'devers-people-{i//100}.json','https://statsapi.mlb.com/api/v1/people?personIds='+','.join(map(str,b))+'&fields=people,id,mlbDebutDate,birthDate,primaryPosition'))
 with concurrent.futures.ThreadPoolExecutor(3) as ex:list(ex.map(fetch,tasks))
def main():
 ensure_cache()
 for f in ['power-translation-v1.json','power-prospect-records.json.gz','power-prospect-catalog.json.gz']:
  SOURCES.append(dict(file=f,sha256=hashlib.sha256((OUT/f).read_bytes()).hexdigest()))
 original=json.loads((OUT/'power-translation-v1.json').read_text());mlb=[r for r in original['seasons'] if r['qualified']];train=[r for r in mlb if r['year']<=2021];val=[r for r in mlb if 2022<=r['year']<=2023];dev=train+val;test=[r for r in mlb if r['year']>=2024]
 survival=[];models={}
 for name,features in [('A',['chase','whiff','hard_hit','barrel']),('B-Barrel',['chase','whiff','barrel']),('B-HardHit',['chase','whiff','hard_hit'])]:
  trials=[]
  for C in [.1,1,10]:
   fit=fit_survival(train,features,C);loss=log_loss([r['endpoint'] for r in val],fit.predict_proba([[r[k] for k in features] for r in val])[:,1]);trials.append((loss,C))
  loss,C=min(trials);fit=fit_survival(dev,features,C);pred=fit.predict_proba([[r[k] for k in features] for r in test])[:,1];models[name]=export_model(fit,dev,features);survival.append(dict(tier=name,features=features,C=C,validationLogLoss=loss,testAUC=float(roc_auc_score([r['endpoint'] for r in test],pred)),testLogLoss=float(log_loss([r['endpoint'] for r in test],pred)),n=len(test),events=sum(r['endpoint'] for r in test)))
 fallback=min([r for r in survival if r['tier']!='A'],key=lambda r:r['validationLogLoss'])['tier']
 # Proxy comparison uses one common, PA-aligned MLB cohort. No source counts
 # are approximated from rounded percentages. Official count inputs require
 # exact PA and HR agreement with TJ's same-ID/same-year record.
 proxy_rows=[];count_rejected=0
 for year in range(2021,2027):
  tj=readcache(f'tj-{year}-mlb.json')['data']['players'];official=readcache(f'devers-mlb-counts-{year}.json')['stats'][0]['splits'];counts=Counter(x['player']['id'] for x in official);by={x['player']['id']:x['stat'] for x in official if counts[x['player']['id']]==1}
  for r in tj:
   if r['pa']<250 or any(r.get(k) is None for k in ['whiff_rate','chase_percent','barrel_percent','hard_hit_percent','pulled_air_percent','fly_ball_percent','iso','launch_speed_90','mean_launch_speed','max_launch_speed']):continue
   o=by.get(r['player_id'])
   if not o or o['plateAppearances']!=r['pa'] or o['homeRuns']!=r['home_run'] or o['atBats']<=o['strikeOuts']:count_rejected+=1;continue
   contact=o['atBats']-o['strikeOuts'];proxy_rows.append(dict(id=r['player_id'],year=year,chase=100*r['chase_percent'],whiff=100*r['whiff_rate'],barrel=100*r['barrel_percent'],hard_hit=100*r['hard_hit_percent'],pullAir=100*r['pulled_air_percent'],air=100*(r['fly_ball_percent']+r.get('line_drive_percent',0)+r.get('pop_up_percent',0)),iso=r['iso'],ev90=r['launch_speed_90'],ev=r['mean_launch_speed'],maxEV=r['max_launch_speed'],hrContact=100*o['homeRuns']/contact,isoContact=(o['doubles']+2*o['triples']+3*o['homeRuns'])/contact,endpoint=r['iso']>=.2 and r['woba_percent']>=.33))
 pt=[r for r in proxy_rows if r['year']<=2023];pv=[r for r in proxy_rows if r['year']==2024];pe=[r for r in proxy_rows if r['year']==2025];future=[r for r in proxy_rows if r['year']==2026]
 specs={'ISO only':['iso'],'Pull-air + air':['pullAir','air'],'ISO + pull-air + air':['iso','pullAir','air'],'HR/contact + pull-air + air':['hrContact','pullAir','air'],'Contact ISO + pull-air + air':['isoContact','pullAir','air'],'EV90 + pull-air':['ev90','pullAir'],'EV90 + pull-air + ISO':['ev90','pullAir','iso'],'EV90 + max EV + pull-air':['ev90','maxEV','pullAir'],'Average EV + pull-air':['ev','pullAir']}
 results=[];pipes={}
 for name,features in specs.items():
  entry=dict(name=name,features=features,targets={})
  for target in ['barrel','hard_hit']:
   trials=[]
   for alpha in [.1,1,10,100]:
    fit=predict_fit(pt,features,target,alpha);pred=fit.predict([[r[k] for k in features] for r in pv]);trials.append((mean_absolute_error([r[target] for r in pv],pred),alpha))
   loss,alpha=min(trials);fit=predict_fit(pt,features,target,alpha);pipes[name,target]=fit
   entry['targets'][target]=dict(alpha=alpha,validation=proxy_metrics(pv,fit.predict([[r[k] for k in features] for r in pv]),target),test2025=proxy_metrics(pe,fit.predict([[r[k] for k in features] for r in pe]),target),sensitivity2026=proxy_metrics(future,fit.predict([[r[k] for k in features] for r in future]),target))
  results.append(entry)
 # No ISO candidate is allowed to win by merely recreating ISO. An outcome-
 # based HR/contact proxy is retained only if validation supports it.
 broad=[r for r in results if r['name'] in ['Pull-air + air','HR/contact + pull-air + air']];best=min(broad,key=lambda r:r['targets']['barrel']['validation']['mae']);tolerance=best['targets']['barrel']['validation']['mae']*1.05;winner=min([r for r in broad if r['targets']['barrel']['validation']['mae']<=tolerance],key=lambda r:len(r['features']));features=winner['features'];fit=pipes[winner['name'],'barrel'];sc,reg=fit.steps[0][1],fit.steps[1][1];co=reg.coef_/sc.scale_;proxy=dict(name=winner['name'],features=features,coefficients=co.tolist(),intercept=float(reg.intercept_-co@sc.mean_),trainingReference={k:sorted(float(r[k]) for r in pt) for k in features},target='Barrel/BBE%',output='Reference impact proxy — not an observed Barrel measurement',validation=winner['targets']['barrel']['validation'],test=winner['targets']['barrel']['test2025']);proxy['publishExperimental']=proxy['validation']['r2']>=.25 and proxy['validation']['rankCorrelation']>=.5
 # Prospect inputs: preserved reviewed source panels plus same-provider raw
 # components needed by the selected proxy. No cross-provider player panel.
 panel=json.loads(gzip.decompress((OUT/'power-prospect-records.json.gz').read_bytes()));catalog=json.loads(gzip.decompress((OUT/'power-prospect-catalog.json.gz').read_bytes()));rawps={}
 for file in CACHE.glob('ps-*.json'):
  for r in readcache(file.name).get('data',[]):
   key=(int(r['id']),int(r['season']),r['level'],r.get('aball_src') if r['level']=='A' else r.get('rk_src') if r['level']=='Rk' else None);rawps[key]=r
 records=[]
 for r in panel['records']:
  z=dict(r);z['pullAir']=r.get('pullAir');z['air']=None;z['hrContact']=None;z['isoContact']=None;z['sourceProxyContactAB']=None
  if r['source']=='Prospect Savant':
   flags=r['rawSourceFlags'];raw=rawps.get((r['mlbamId'],r['year'],flags['level'],flags.get('aball_src') if flags['level']=='A' else flags.get('rk_src') if flags['level']=='Rk' else None))
   if raw:
    den=(raw.get('ab') or 0)-(raw.get('k') or 0);air=sum(float(raw.get(k) or 0) for k in ['fbrate','ldrate']);allbatted=sum(float(raw.get(k) or 0) for k in ['fbrate','ldrate','gbrate'])
    if den>0:
     z['sourceProxyContactAB']=den;z['hrContact']=100*raw['hr']/den;z['isoContact']=(raw['doubles']+2*raw['triples']+3*raw['hr'])/den
    if allbatted>0:z['air']=air
    else:z['pullAir']=None
  records.append(z)
 # Existing TJ records keep their measurements; the broad proxy cannot borrow
 # AB/K from PS or from mismatched official samples, so unknown stays unknown.
 people={}
 for p in CACHE.glob('devers-people-*.json'):people.update({r['id']:r for r in readcache(p.name)['people']})
 for p in catalog['players']:
  info=people.get(p['mlbamId']);p['debutKnown']=info is not None;p['mlbDebutDate']=info.get('mlbDebutDate') if info else None
  if info and info.get('birthDate'):p['birthDate']=info['birthDate']
 # All percentile normalization pools are same-season, same-level/environment,
 # same-provider, 100+ PA. Age bands are optional if at least 50 records.
 groups=defaultdict(list)
 for r in records:
  if r['pa']>=100:groups[(r['year'],r['level'],r['source'])].append(r)
 reference=models['A']['reference'];mlbref=reference
 def ageband(r):
  age=r.get('seasonAge') if r.get('seasonAge') is not None else r.get('providerAge')
  return None if age is None else '18 and under' if age<19 else '19–20' if age<21 else '21–22' if age<23 else '23–24' if age<25 else '25+'
 tier_counts=Counter();failures=Counter()
 for r in records:
  r['tier']='D';r['devers']=None;r['scoreReason']='100+ source PA required.';r['ageBand']=ageband(r)
  if r['pa']<100:failures['sample']+=1;continue
  pool=groups[r['year'],r['level'],r['source']];agepool=[v for v in pool if ageband(v)==r['ageBand']] if r['ageBand'] else [];reliableImpact=(r.get('trackedBBE') or 0)>=50
  required=['chase','whiff']+(['hard_hit','barrel'] if reliableImpact and r.get('hard_hit') is not None and r.get('barrel') is not None else ['barrel'] if reliableImpact and r.get('barrel') is not None else ['hard_hit'] if reliableImpact and r.get('hard_hit') is not None else features)
  useAge=len(agepool)>=50 and all(sum(v.get(k) is not None and (k not in ['hard_hit','barrel'] or (v.get('trackedBBE') or 0)>=50) for v in agepool)>=30 for k in required)
  if useAge:pool=agepool
  r['normalization']=dict(year=r['year'],level=r['level'],source=r['source'],ageBand=r['ageBand'] if useAge else None,n=len(pool));r['ageContext']='age-band percentiles' if useAge else 'age shown as context; insufficient age-band sample'
  if len(pool)<30:r['scoreReason']='Fewer than 30 same-environment normalization records.';failures['cohort']+=1;continue
  def align(k,distribution):
   if r.get(k) is None or k in ['hard_hit','barrel'] and not reliableImpact:return None,None
   values=[v[k] for v in pool if v.get(k) is not None and math.isfinite(v[k]) and (k not in ['hard_hit','barrel'] or (v.get('trackedBBE') or 0)>=50)]
   if len(values)<30:return None,None
   p=pctile(values,r[k]);return quantile(distribution,p),100*p
  aligned={};percentiles={}
  for k in ['chase','whiff','hard_hit','barrel']:
   aligned[k],percentiles[k]=align(k,mlbref[k])
  if aligned['chase'] is None or aligned['whiff'] is None:r['scoreReason']='Chase and Whiff both required; no substitute or zero-fill.';failures['discipline']+=1;continue
  if aligned['hard_hit'] is not None and aligned['barrel'] is not None:tier='A';modelKey='A'
  elif aligned['barrel'] is not None or aligned['hard_hit'] is not None:
   tier='B';modelKey=fallback if aligned['barrel' if fallback=='B-Barrel' else 'hard_hit'] is not None else 'B-Barrel' if aligned['barrel'] is not None else 'B-HardHit'
  else:
   r['impactSampleReason']='Measured impact requires 50+ tracked batted-ball events; unknown or smaller samples are not used.' if not reliableImpact else 'Measured impact normalization cohort is insufficient.'
   if (r.get('sourceProxyContactAB') or 0)<50:r['scoreReason']='Impact proxy requires 50+ observed non-strikeout at-bats in the same source record.';failures['proxySample']+=1;continue
   if not proxy['publishExperimental']:r['scoreReason']='Impact proxy did not meet predeclared validation guard.';failures['proxyValidation']+=1;continue
   proxyAligned={};proxyPct={}
   for k in features:proxyAligned[k],proxyPct[k]=align(k,proxy['trainingReference'][k])
   if any(v is None for v in proxyAligned.values()):r['scoreReason']='Impact proxy inputs or normalization coverage unavailable.';failures['proxyInputs']+=1;continue
   estimate=proxy['intercept']+sum(c*proxyAligned[k] for k,c in zip(features,proxy['coefficients']));aligned['barrel']=max(0,min(100,estimate));r['proxy']=dict(impactPercentile=100*pctile(mlbref['barrel'],aligned['barrel']),name=proxy['name'],components={k:r[k] for k in features},componentPercentiles=proxyPct,referenceImpact=aligned['barrel'],testMAE=proxy['test']['mae']);tier='C';modelKey='B-Barrel'
  model=models[modelKey];means=dict(zip(model['features'],model['means']));coef=dict(zip(model['features'],model['coefficients']));risk=-sum(coef[k]*(aligned[k]-means[k]) for k in ['chase','whiff']);impact=sum(coef[k]*(aligned[k]-means[k]) for k in model['features'] if k not in ['chase','whiff']);baseline=model['intercept']+sum(coef[k]*means[k] for k in model['features']);margin=baseline+impact-risk;score=50+50*math.tanh(margin/(2*model['marginScale']));r.update(tier=tier,modelKey=modelKey,devers=round(score,1),margin=margin,risk=risk,impact=impact,baseline=baseline,aligned=aligned,percentiles=percentiles,scoreReason=None,confidence={'A':'Full metric coverage','B':'Moderate metric coverage','C':'Experimental impact proxy'}[tier],frontierPosition='above' if margin>.05 else 'below' if margin<-.05 else 'near')
  if tier=='C':
   error=abs(coef['barrel'])*proxy['test']['mae'];r['proxySensitivity']=[round(50+50*math.tanh(v/(2*model['marginScale'])),1) for v in [margin-error,margin+error]]
  tier_counts[tier]+=1
 # MLB references and distance candidates use raw development units, not MiLB
 # rates. These are component neighbors and same-season endpoints, not careers.
 anchor_names=['Aaron Judge','Shohei Ohtani','Rafael Devers','Matt Olson','Kyle Schwarber','James Wood','Pete Crow-Armstrong','Joey Gallo','Juan Soto','Bryce Harper','Max Muncy','Oneil Cruz'];anchors=[]
 for name in anchor_names:
  options=[r for r in mlb if r['name']==name and (name!='Max Muncy' or r['playerId']==571970)]
  if options:anchors.append(options[0]['playerId']);ref=[]
 for pid in anchors:
  rows=sorted([p for p in mlb if p['playerId']==pid and p['year']<=2026],key=lambda p:p['year'],reverse=True)
  if rows:ref.append(rows[0])
 pool=[p for p in mlb if p['year']==2026];pool.sort(key=lambda p:p['barrel'])
 for i in np.linspace(0,len(pool)-1,25-len(ref),dtype=int):
  if pool[i]['id'] not in {p['id'] for p in ref}:ref.append(pool[i])
 for p in pool:
  if len(ref)>=25:break
  if p['id'] not in {v['id'] for v in ref}:ref.append(p)
 extreme=[]
 for period,rs in [('Development 2015–2023',dev),('Inspected holdout 2024–2026',test)]:
  for w,c in [(30,30),(30,35),(35,35)]:
   for metric,bands in [('barrel',[(0,8),(8,12),(12,100)]),('hard_hit',[(0,40),(40,50),(50,100)])]:
    for low,high in bands:
     sub=[r for r in rs if r['whiff']>=w and r['chase']>=c and low<=r[metric]<high];extreme.append(dict(period=period,minWhiff=w,minChase=c,metric=metric,low=low,high=high,n=len(sub),events=sum(r['endpoint'] for r in sub),rate=sum(r['endpoint'] for r in sub)/len(sub) if sub else None))
 report=dict(asOf=DATE,name='DEVERS',description='Experimental impact-relative-to-Chase-and-Whiff profile index. Not a probability or MLB-equivalent projection.',models=models,fallback=fallback,survivalResearch=survival,proxy=proxy,proxyResearch=results,proxySample=dict(train=len(pt),validation=len(pv),test2025=len(pe),sensitivity2026=len(future),unalignedCountsExcluded=count_rejected),normalization='Within season × level/tracking environment × provider, 100+ PA; age band only with ≥50 records; ≥30 observed values per input. Percentiles align to historical qualified MLB development distributions for a relative index, not a translation.',scoreFormula='50 + 50*tanh(fitted margin / (2*development margin SD)); margin=0 maps to 50. This display scaling is a convention, not a fitted probability or a validated scouting threshold.',tierCounts=dict(tier_counts),unscored=dict(failures),sources=SOURCES,extreme=extreme,limits=['All survival validation is same-season MLB endpoint classification; it is not future prospect validation.','Proxy evaluation is MLB-only and PA-aligned; AA/High-A/Rookie transfer is unvalidated.','Proxy HR per non-strikeout AB is outcome- and environment-dependent; it is not measured contact quality.','Percentile alignment removes cohort location/scale differences, not ballpark, competition or MLB translation effects.','Confidence badges describe input coverage, not calibrated statistical certainty.','The four-metric conditional Chase/Hard-Hit coefficients can have counterintuitive signs due to correlated inputs; they are not causal skill penalties.','Scores across tiers are approximate and should be inspected with tier filters.','Proxy sensitivity is ±one held-out MAE propagated through the index, not a confidence interval.','Unknown debut status is excluded from the non-debuted leaderboard. Player search remains broader.','No main rankings, grades, recommendations or player profiles use DEVERS.'])
 keep={'id','mlbamId','name','year','level','pa','chase','whiff','hard_hit','barrel','source','sourceUrl','sourceManifest','retrieved','seasonAge','providerAge','swings','outsidePitches','trackedBBE','providerBIP','pullAir','air','hrContact','isoContact','tier','devers','scoreReason','ageBand','normalization','ageContext','modelKey','confidence','margin','risk','impact','baseline','aligned','percentiles','proxy','proxySensitivity','frontierPosition','impactSampleReason','sourceProxyContactAB'}
 records=[{k:v for k,v in r.items() if k in keep} for r in records]
 dump('devers-research',report);dump('devers-records',dict(asOf=DATE,records=records,players=catalog['players'],references=ref,mlbSeasons=mlb));print(json.dumps(dict(fallback=fallback,survival=survival,proxy=proxy,proxySample=report['proxySample'],tiers=dict(tier_counts),unscored=dict(failures)),indent=2))
if __name__=='__main__':main()

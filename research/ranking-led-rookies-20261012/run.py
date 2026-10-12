"""Ranking-led dynasty policy research. Never writes production files."""
import json,csv,sys,gzip,base64,re,copy,math,hashlib,collections
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.isotonic import IsotonicRegression
D=Path(__file__).resolve().parent;ROOT=D.parents[1];MODEL=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(MODEL/'trade-preview-v23c-evidence-guard'));import model_asset_fit as m
r=m.r;old=m.old
src=list(csv.DictReader((D/'Supplied_Rankings.tsv').open(),delimiter='\t'))
for x in src:x.update(id=x['Player ID'].strip('*'),rank=int(x['Ranking']),tier=int(x['Tier']),family='P' if any(z in x['Position'].split(',') for z in ['P','SP','RP']) else 'H')
assert len(src)==500 and len({x['id'] for x in src})==500 and sorted(x['rank'] for x in src)==list(range(1,501))
cat=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])))
assets={a['id']:a for a in cat['assets']};AP=m.v.appearance_history()
H={};P={};first={};hist=collections.defaultdict(list)
for a in old.AN:
 z=copy.deepcopy(a);family='H' if z['role']=='H' else 'P'
 if family=='P':z['role']=m.v.observed_role(AP.get((z['id'],z['year']),{}),z['role'])
 (H if family=='H' else P)[z['id'],z['year']]=z;hist[z['id'],family].append(z)
 if r.exposure(z['stat'],z['role'])>0:first[z['id'],family]=min(first.get((z['id'],family),9999),z['year'])

def talent(s,rr):
 v=old.vector(s,rr,old.refs)/old.dens['H' if rr=='H' else 'P']
 return float(sum(v[k] for k in ([0,3,4,5] if rr=='H' else [0,1,4,5])))
# Frozen role-reference workloads and calibration counts, corrected observed roles.
CAL={rr:sorted(talent({k:v*r.REFERENCE[rr]/r.exposure(z['stat'],rr) for k,v in z['stat'].items()},rr) for z in list(H.values())+list(P.values()) if z['role']==rr and z['year']<=2012 and old.QUAL(z)) for rr in ['H','SP','RP']}
assert all(len(x)>=20 for x in CAL.values())
def percentile(q,rr):return float((np.searchsorted(CAL[rr],q,side='left')+np.searchsorted(CAL[rr],q,side='right'))/2/len(CAL[rr]))
def rank_model(q,rr):
 family='H' if rr=='H' else 'P';positions=[x['rank'] for x in src if x['family']==family]
 quantile=percentile(q,rr);index=(1-quantile)*(len(positions)-1)
 return float(np.interp(index,np.arange(len(positions)),positions)),quantile

def weight(e,k,supported=True):return .5*e/(e+k) if supported else 0.
def adjust(rank,modelrank,e,k,lo=1,hi=500,supported=True):
 w=weight(e,k,supported);result=math.exp((1-w)*math.log(rank)+w*math.log(modelrank));return min(hi,max(lo,result)),w

anchor=[]
for x in src:
 a=assets.get(x['id']);p=old.players.get(x['id'])
 if not a or not p or a['audit']['kind']!='prospect' or a['values']['neutral']['display'] is None or x['ETA']=='Debuted':continue
 family=x['family'];rr='H' if family=='H' else m.v.role(p)
 if any(r.exposure(z['stat'],z['role'])>0 for z in m.v.seasons(p,rr) if ('H' if z['role']=='H' else 'P')==family):continue
 anchor.append({'id':x['id'],'rank':x['rank'],'production':a['values']['neutral']['display']})
assert len(anchor)>=50
iso=IsotonicRegression(increasing=False,out_of_bounds='clip').fit([x['rank'] for x in anchor],[x['production'] for x in anchor])
curve=[{'rank':k,'value':float(iso.predict([k])[0])} for k in range(1,501)]
tiers={tier:(min(x['rank'] for x in src if x['tier']==tier),max(x['rank'] for x in src if x['tier']==tier)) for tier in {x['tier'] for x in src}}
rows=[];unsupported=[];details=[]
for x in src:
 a=assets.get(x['id']);p=old.players.get(x['id']);base=a['values']['neutral']['display'] if a else None
 row={'id':x['id'],'name':x['Player'],'source_rank':x['rank'],'source_tier':x['tier'],'source_ETA':x['ETA'],'family':x['family'],'production':base,'source_only_value':float(iso.predict([x['rank']])[0]),'status':'unsupported outside current catalog'}
 if not a or not p or base is None or a['audit']['kind']=='unmodeled':
  # Curve point is illustrative only and is not assigned as an asset value.
  row['source_only_value']=None;unsupported.append({'id':x['id'],'name':x['Player'],'rank':x['rank'],'reason':'Missing currently modeled catalog identity'});rows.append(row);continue
 rr=m.v.role(p);family='H' if rr=='H' else 'P';seasons=m.v.seasons(p,rr)
 exposure=sum(r.exposure(z['stat'],rr) for z in seasons if z['role']==rr);forecast=m.v.recent_forecast(p,rr)
 status='source anchor only';q=None;mr=float(x['rank']);quantile=None;supported=False
 if family==x['family'] and forecast and not a['audit'].get('two_way_components'):
  rates,work,audit=forecast
  gp=p.get('pit',{}).get('GP',0);gs=p.get('pit',{}).get('GS',0)
  # Fewer than10 appearances and mixed roles do not justify a future pitching role.
  roleok=rr=='H' or (gp>=10 and (gs==0 or gs/gp>=.8))
  if roleok:
   signal={k:v*r.REFERENCE[rr] for k,v in rates.items()}
   if rr=='H':signal=m.v.reconcile(signal)
   q=talent(signal,rr);mr,quantile=rank_model(q,rr);supported=True;status='ranking-led talent deviation supported'
  else:status='source anchor; pitching role evidence insufficient or mixed'
 if exposure==0:status='source anchor; no positive MLB evidence';supported=False
 lower=tiers[max(min(tiers),x['tier']-1)][0];upper=tiers[min(max(tiers),x['tier']+1)][1]
 row.update(status=status,role=rr,career_exposure=exposure,talent_percentile=quantile,model_rank_signal=mr,minimum_adjusted_rank=lower,maximum_adjusted_rank=upper)
 for k in ([150,300,600,1200] if rr=='H' else [42.5,85,170,340]):
  er,w=adjust(x['rank'],mr,exposure,k,lower,upper,supported);val=float(iso.predict([er])[0]);label=str(k).replace('.','p')
  row['K'+label+'_value']=val;row['K'+label+'_rank']=er;row['K'+label+'_model_weight']=w
  assert 0<=w<.5 and lower<=er<=upper and val>=0
 ref=600 if rr=='H' else 170;label=str(ref);row.update(reference_value=row['K'+label+'_value'],reference_adjusted_rank=row['K'+label+'_rank'],reference_model_weight=row['K'+label+'_model_weight'],reference_source_weight=1-row['K'+label+'_model_weight'],value_delta=row['K'+label+'_value']-base)
 rows.append(row);details.append({'id':x['id'],'name':x['Player'],'source':{k:x[k] for k in ['rank','tier','ETA','Position','Team','Age']},'talent_signal':q,'projected_rates_unchanged':True,'source_publication_date':'unknown','source_model_evidence_overlap':'same-snapshot disagreement; not independent Bayesian information','explanation':status})
# Rankings across the existing calculator universe are sensitivities, not production writes.
by={x['id']:x for x in rows}
for method in ['production','reference']:
 universe=[]
 for a in cat['assets']:
  value=a['values']['neutral']['display'];x=by.get(a['id'])
  if method=='reference' and x and x.get('reference_value') is not None:value=x['reference_value']
  if value is not None:universe.append((a['id'],value))
 ranks={ident:i+1 for i,(ident,value) in enumerate(sorted(universe,key=lambda z:(-z[1],z[0])))}
 for x in rows:
  if x['id'] in ranks:x[method+'_calculator_rank']=ranks[x['id']]

# Past-only proxy comparison. No 2026 source ranks or future observations in predictors.
historical=[]
for (ident,family),firstyear in sorted(first.items()):
 if firstyear<2013:continue #2010-12 category scales precede every forecast.
 dated=[x for x in old.CO if x['mlbamId']==ident and bool(x['pitcher'])==(family=='P') and x['year']<=firstyear]
 for origin in [firstyear,firstyear+1]:
  if origin>2022 or not dated:continue
  eligible=[x for x in dated if origin-x['year']<=2]
  if not eligible:continue
  source=max(eligible,key=lambda x:x['year']);index=H if family=='H' else P;current=index.get((ident,origin))
  if not current or r.exposure(current['stat'],current['role'])<=0:continue
  rr=current['role'];history=[a for a in hist[ident,family] if a['year']<=origin and a['role']==rr and r.exposure(a['stat'],rr)>0]
  e=sum(r.exposure(a['stat'],rr) for a in history)
  if e>(600 if rr=='H' else 170):continue
  recent=[a for a in history if origin-3<=a['year']<=origin]
  weights={origin-3:.1,origin-2:.2,origin-1:.3,origin:.4};mass=sum(weights[a['year']] for a in recent)
  recentex=sum(weights[a['year']]*r.exposure(a['stat'],rr) for a in recent)/mass;strength=100 if rr=='H' else 30
  rates={k:(sum(weights[a['year']]*a['stat'].get(k,0) for a in recent)/mass+strength*old.prior[rr][k])/(recentex+strength) for k in old.fields[rr]}
  signal={k:v*r.REFERENCE[rr] for k,v in rates.items()}
  if rr=='H':signal=m.v.reconcile(signal)
  q=talent(signal,rr);quantile=percentile(q,rr);modelrank=1+99*(1-quantile)
  ap=AP.get((ident,origin),{});gp=ap.get('GP',0);gs=ap.get('GS',0);supported=rr=='H' or (gp>=10 and (gs==0 or gs/gp>=.8))
  actual=sum(.88**t*r.utility(r.surplus(index.get((ident,origin+t+1),{}).get('stat',{}),index.get((ident,origin+t+1),{}).get('role',rr))) for t in range(3))
  row={'id':ident,'name':current['name'],'origin':origin,'rank_year':source['year'],'source_rank':source['rank'],'source_age_years':origin-source['year'],'role':rr,'family':family,'career_exposure':e,'actual_three_year_contribution':actual,'model_rank_signal':modelrank,'model_supported':supported,'stage':'development' if origin<=2015 else 'later','small_debut':e<(250 if rr=='H' else 50)}
  for label,k in [('fast',150 if rr=='H' else 42.5),('medium',300 if rr=='H' else 85),('reference',600 if rr=='H' else 170),('slow',1200 if rr=='H' else 340)]:row[label+'_rank'],row[label+'_weight']=adjust(source['rank'],modelrank,e,k,1,100,supported)
  historical.append(row)

def metric(xs):
 result={'n':len(xs),'players':len({a['id'] for a in xs}),'origins':dict(collections.Counter(a['origin'] for a in xs))}
 for method in ['source','model','fast','medium','reference','slow']:
  key={'source':'source_rank','model':'model_rank_signal'}.get(method,method+'_rank');v=[-a[key] for a in xs];actual=[a['actual_three_year_contribution'] for a in xs]
  pairs=[]
  for i,a in enumerate(xs):
   for b in xs[i+1:]:
    if a['origin']!=b['origin'] or a['id']==b['id'] or a['actual_three_year_contribution']==b['actual_three_year_contribution']:continue
    change=b[key]-a[key];truth=a['actual_three_year_contribution']-b['actual_three_year_contribution'];pairs.append(.5 if change==0 else float(change*truth>0))
  result[method]={'Spearman':float(spearmanr(v,actual).statistic) if len(xs)>2 and len(set(v))>1 and len(set(actual))>1 else None,'within_origin_pair_accuracy':float(np.mean(pairs)) if pairs else None,'pairs':len(pairs)}
 return result
metrics={stage:{group:metric([a for a in historical if a['stage']==stage and (group=='all' or group=='small_debut' and a['small_debut'] or group in ['H','SP','RP'] and a['role']==group)]) for group in ['all','small_debut','H','SP','RP']} for stage in ['development','later']}
# Cluster bootstrap for differences in within-origin discrimination, all later cases.
xs=[a for a in historical if a['stage']=='later'];ids=sorted({a['id'] for a in xs});rng=np.random.default_rng(121026);boot=[]
for _ in range(500):
 chosen=rng.choice(ids,len(ids),replace=True) if ids else [];sample=[a for ident in chosen for a in xs if a['id']==ident];out=metric(sample)
 if out.get('reference',{}).get('within_origin_pair_accuracy') is not None:boot.append(out['reference']['within_origin_pair_accuracy']-out['source']['within_origin_pair_accuracy'])
# Frozen continuity checks use a hypothetical fixed signal rather than changing talent at debut.
continuity=[]
for name,rank,modelrank,k in [('Josue De Paula',3,200,600),('Kaelen Culpepper',41,200,600),('Pitcher fixture',9,80,170)]:
 for exposure in [0,1e-9,1,10,42,128,250,600,1200]:
  er,w=adjust(rank,modelrank,exposure,k);continuity.append({'name':name,'exposure':exposure,'adjusted_rank':er,'source_weight':1-w,'value':float(iso.predict([er])[0])})
 assert abs(adjust(rank,modelrank,1e-9,k)[0]-rank)<1e-8

def write(name,x):(D/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(name,x):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in x for k in a)));w.writeheader();w.writerows(x)
csvwrite('Current_Comparison.csv',rows);csvwrite('Debuted_Examples.csv',[a for a in rows if a['source_ETA']=='Debuted']);csvwrite('Largest_Changes.csv',sorted([a for a in rows if a.get('value_delta') is not None],key=lambda a:-abs(a['value_delta']))[:30]);csvwrite('Historical_Comparisons.csv',historical);csvwrite('Transition_Checks.csv',continuity);csvwrite('Unsupported.csv',unsupported)
write('Rank_Value_Curve.json',{'anchor_n':len(anchor),'calibration':'Internal deployed pure-prospect value scale, not transaction or performance truth','anchor_assets':anchor,'curve':curve});write('Current_Evidence.json',details)
write('Historical_Results.json',{'metrics':metrics,'reference_minus_source_pair_accuracy_95pct':list(np.quantile(boot,[.025,.975])) if boot else None,'limitations':['Exposed preserved FG ranks differ from supplied fantasy provider','Three-year contribution discrimination is not eight-year price accuracy','Source freshness<=2years sharply restricts later coverage','Incomplete historic source files require generic top100 model-rank proxy','First-year-only and rate signals have different forecast quantities; no regression fit on targets']})
write('Verification.json',{'protocol_sha256':hashlib.sha256((D/'Protocol.json').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((D/'Supplied_Rankings.tsv').read_bytes()).hexdigest(),'production_html_sha256':hashlib.sha256((ROOT/'trade-analyzer-beta/index.html').read_bytes()).hexdigest(),'supplied':500,'source_marked_debuted':sum(a['ETA']=='Debuted' for a in src),'matched':sum(a.get('reference_value') is not None for a in rows),'matched_debuted':sum(a['source_ETA']=='Debuted' and a.get('reference_value') is not None for a in rows),'anchor_assets':len(anchor),'unsupported':len(unsupported),'historical_cases':len(historical),'zero_exposure_continuity_pass':True,'all_source_weights_above_half':True,'underlying_projections_and_production_unchanged':True,'source_publication_date':'unknown','production_adoption':False})
verification=json.loads((D/'Verification.json').read_text())
verification['input_hashes']={str(f.relative_to(MODEL)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [MODEL/'trade-preview-v23c-evidence-guard/model_asset_fit.py',MODEL/'trade-preview-v23/model_v23.py',MODEL/'trade-preview-v22/model/inputs/annual-components.json',MODEL/'trade-preview-v22/model/inputs/delayed-arrival-diagnostic.json',MODEL/'trade-preview-v23c-evidence-guard/Recovery_Appearances.json']}
verification['no_verified_optimal_strength']=True
write('Verification.json',verification)
print(json.dumps({'coverage':json.loads((D/'Verification.json').read_text()),'later':metrics['later'],'examples':[a for a in rows if a['name'] in ['Josue De Paula','Leo De Vries','Kaelen Culpepper','Walker Jenkins','Kade Anderson','Emmanuel Rodriguez']]},indent=2))

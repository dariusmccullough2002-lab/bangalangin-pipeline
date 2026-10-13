"""Separate arrival survival and conditional MLB workload; no price adjustments."""
from pathlib import Path
import json,gzip,math,datetime,collections,re,base64,csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from scipy.optimize import minimize_scalar
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
CO=json.loads((OUT/'inputs/Ranked_Snapshots.json').read_text());HIST=json.load(gzip.open(OUT/'inputs/Historical_Seasons.json.gz','rt'));END=HIST['asOf']
AN={(a['mlbamId'],a['year'],a['family']):a['stats'] for a in HIST['seasons']};FIRST={int(i):y for i,y in HIST['first_mlb_year'].items()}
LEVEL={'DSL':0,'R':0,'CPX':0,'ACL':0,'FCL':0,'A-':1,'A':2,'A+':3,'AA':4,'AAA':5,'MLB':6}
def age(a):
 if a.get('age') is not None:return float(a['age'])
 if a.get('birthDate'):return (datetime.date(a['year'],4,1)-datetime.date.fromisoformat(a['birthDate'])).days/365.25
 return float(a.get('published_age') or 22)
def fam(a):return 'P' if a['pitcher'] else 'H'
def exposure(i,y,f):return AN.get((i,y,f),{}).get('PA' if f=='H' else 'IP',0.)
def first(a):
 i=a['mlbamId'];f=fam(a)
 if FIRST.get(i,9999)<2010:return FIRST[i]
 years=[y for y in range(2010,END+1) if exposure(i,y,f)>0]
 return min(years) if years else None
def eligible(a):return first(a) is None or first(a)>=a['year']
def regular(a,y):
 s=AN.get((a['mlbamId'],y,fam(a)),{});f=fam(a)
 if f=='H':return s.get('PA',0)>=(300 if a.get('position')=='C' else 400)
 return s.get('IP',0)>=(80 if s.get('GS',0)>=5 else 40)
def features(a,lag,ranked=True):
 level=LEVEL.get(a.get('level'),2.5);known=a.get('level') in LEVEL
 row=[age(a)+lag,level,float(not known),float(lag),float(lag)**2]
 if ranked:row+=[math.log(max(1,float(a['rank'])))]
 return row

def train_arrival(end,C=1,ranked=True):
 samples=[a for a in CO if a['year']<=end and eligible(a)];counts=collections.Counter(a['mlbamId'] for a in samples);models={};baselines={};support={}
 for f in ['H','P']:
  X=[];Y=[];W=[];lags=collections.defaultdict(lambda:[0.,0.])
  for a in samples:
   if fam(a)!=f:continue
   event=first(a)
   for y in range(a['year'],min(end,event if event is not None else end)+1):
    lag=y-a['year'];event_here=int(event==y);w=1/counts[a['mlbamId']];X.append(features(a,lag,ranked));Y.append(event_here);W.append(w);lags[lag][0]+=event_here*w;lags[lag][1]+=w
  model=make_pipeline(StandardScaler(),LogisticRegression(C=C,max_iter=1000));model.fit(X,Y,logisticregression__sample_weight=W);models[f]=model
  pooled=(sum(Y)+.5)/(len(Y)+1);baselines[f]={t:(event+.5+2*pooled)/(risk+1+2) for t,(event,risk) in lags.items()};support[f]={'players':len({a['mlbamId'] for a in samples if fam(a)==f}),'risk_rows':len(Y),'events':sum(Y),'max_training_lag':max(lags),'max_source_rank':max(a['rank'] for a in samples if fam(a)==f)}
 return {'end':end,'C':C,'ranked':ranked,'models':models,'baseline':baselines,'support':support}
def arrival(a,fit,horizon=8,baseline=False):
 masses=[];survival=1.;f=fam(a);support=fit['support'][f]
 for t in range(horizon):
  if baseline:p=fit['baseline'][f].get(t,fit['baseline'][f][support['max_training_lag']])
  else:p=float(fit['models'][f].predict_proba([features(a,t,fit['ranked'])])[0,1])
  p=min(1,max(0,p));masses.append(survival*p);survival*=1-p
 return np.array(masses),float(survival)

def donors(end):
 samples=[a for a in CO if a['year']<=end and eligible(a) and first(a) is not None and first(a)<=end];counts=collections.Counter(a['mlbamId'] for a in samples);out=[]
 for a in samples:
  debut=first(a)
  # 2020 volume is not an ordinary debut season; retain as a right-censoring break.
  if debut==2020:continue
  span=min(8,end-debut+1);observed=[]
  for t in range(span):observed.append(None if debut+t==2020 else exposure(a['mlbamId'],debut+t,fam(a)))
  event=next((t for t in range(span) if debut+t!=2020 and regular(a,debut+t)),None)
  out.append({'a':a,'debut':debut,'duration':span,'workload':observed,'event':event,'weight':1/counts[a['mlbamId']]})
 return out

def workload(a,debutlag,pool,k=60,ranked=True):
 f=fam(a);sample=[d for d in pool if fam(d['a'])==f];target=np.array([age(a)+debutlag,LEVEL.get(a.get('level'),2.5)]+([math.log(max(1,a['rank']))] if ranked else [])+([3*float(a.get('prior_milb_start_fraction') if a.get('prior_milb_start_fraction') is not None else .5)] if f=='P' else []))
 X=np.array([[age(d['a'])+d['debut']-d['a']['year'],LEVEL.get(d['a'].get('level'),2.5)]+([math.log(max(1,d['a']['rank']))] if ranked else [])+([3*float(d['a'].get('prior_milb_start_fraction') if d['a'].get('prior_milb_start_fraction') is not None else .5)] if f=='P' else []) for d in sample]);scale=np.maximum(np.std(X,axis=0),.5);dist=np.sqrt(np.sum(((X-target)/scale)**2,axis=1));order=np.argsort(dist);chosen=order[:min(k,len(order))];weights=np.array([sample[j]['weight'] for j in chosen])*np.exp(-dist[chosen]);weights/=sum(weights);sample=[sample[j] for j in chosen];means=[];active=[];firstregular=[];survival=1.;support=[]
 for t in range(8):
  ix=[j for j,d in enumerate(sample) if t<d['duration'] and d['workload'][t] is not None];ws=weights[ix];vals=np.array([sample[j]['workload'][t] for j in ix]);mass=float(sum(ws))
  means.append(float(ws@vals/mass) if mass else None);active.append(float(ws@(vals>0)/mass) if mass else None);support.append(len({sample[j]['a']['mlbamId'] for j in ix}))
  risk=[j for j,d in enumerate(sample) if t<d['duration'] and (d['event'] is None or d['event']>=t) and d['workload'][t] is not None];riskmass=sum(weights[risk]);ev=sum(weights[j] for j in risk if sample[j]['event']==t);haz=float(ev/riskmass) if riskmass else 0.;firstregular.append(survival*haz);survival*=1-haz
 return {'mean':means,'active':active,'regular_mass':firstregular,'no_regular_by_8':survival,'support':support,'donor_players':len({d['a']['mlbamId'] for d in sample})}

def forecast(a,fit,pool,k=60,baseline=False):
 mass,noarrival=arrival(a,fit,baseline=baseline);annual=[];regularcdf=0.;regularmass=[];work=[];act=[];supports=[]
 cond=[workload(a,j,pool,k,fit['ranked']) for j in range(8)]
 for t in range(8):
  values=[mass[j]*(cond[j]['mean'][t-j] or 0) for j in range(t+1)];work.append(float(sum(values)));act.append(float(sum(mass[j]*(cond[j]['active'][t-j] or 0) for j in range(t+1))));rm=float(sum(mass[j]*cond[j]['regular_mass'][t-j] for j in range(t+1)));regularmass.append(rm);regularcdf+=rm;supports.append(min(cond[j]['support'][t-j] for j in range(t+1)))
  annual.append({'year':a['year']+t,'first_mlb_probability':float(mass[t]),'mlb_arrived_by_year':float(sum(mass[:t+1])),'mlb_active_probability':act[-1],'expected_workload':work[-1],'regular_role_reached_by_year':regularcdf,'minimum_workload_support_players':supports[-1]})
 return {'annual':annual,'no_mlb_by_horizon_probability':noarrival,'first_regular_mass':regularmass,'regular_not_reached_by_horizon_probability':float(1-sum(regularmass)),'conditional_debut_year_workload':cond[0]['mean'][0],'conditional_first_year_regular_probability':cond[0]['regular_mass'][0],'conditional_support':cond[0]['support']}

def brier(a,pred,end):
 ev=first(a);rs=[]
 for t,row in enumerate(pred['annual']):
  if row['year']>end:break
  rs.append((row['mlb_arrived_by_year']-int(ev is not None and ev<=row['year']))**2)
 return rs

def select(ranked=True):
 results=[]
 for C in [.1,1.,10.]:
  errors=[]
  for origin in [2014,2015]:
   fit=train_arrival(origin-1,C,ranked=ranked);pool=donors(origin-1)
   for a in CO:
    if a['year']==origin and eligible(a):
     m,_=arrival(a,fit);ev=first(a)
     for t in range(min(8,2018-origin+1)):errors.append((sum(m[:t+1])-int(ev is not None and ev<=origin+t))**2)
  results.append({'C':C,'brier':float(np.mean(errors)),'n':len(errors)})
 chosen=min(results,key=lambda x:x['brier'])['C'];ks=[]
 for k in [30,60,120]:
  errors=[]
  for origin in [2014,2015]:
   pool=donors(origin-1)
   for a in CO:
    if a['year']!=origin or not eligible(a):continue
    ev=first(a)
    if ev is None or ev>2018:continue
    pred=workload(a,ev-origin,pool,k,ranked)
    for t,v in enumerate(pred['mean']):
     if ev+t>2018 or v is None:break
     errors.append(abs(v-exposure(a['mlbamId'],ev+t,fam(a))))
  ks.append({'neighbors':k,'MAE_mixed_units_selection_only':float(np.mean(errors)),'n':len(errors)})
 # H/P selection uses normalized role volume to avoid choosing k on mixed PA/IP units.
 for record in ks:
  errs=[]
  for origin in [2014,2015]:
   pool=donors(origin-1)
   for a in CO:
    if a['year']!=origin or not eligible(a):continue
    ev=first(a)
    if ev is None or ev>2018:continue
    pred=workload(a,ev-origin,pool,record['neighbors'],ranked)
    for t,v in enumerate(pred['mean']):
     if ev+t>2018 or v is None:break
     errs.append(abs(v-exposure(a['mlbamId'],ev+t,fam(a)))/(509 if fam(a)=='H' else 171))
  record['normalized_MAE']=float(np.mean(errs))
 return {'arrival_candidates':results,'workload_candidates':ks,'C':chosen,'neighbors':min(ks,key=lambda x:x['normalized_MAE'])['neighbors'],'selection_outcome_end':2018,'ranked':ranked}

def calibrate_regular(selection):
 values={'H':[],'P':[]}
 for origin in [2014,2015]:
  fit=train_arrival(origin-1,selection['C'],selection['ranked']);pool=donors(origin-1)
  for a in CO:
   if a['year']!=origin or not eligible(a):continue
   pred=forecast(a,fit,pool,selection['neighbors'])
   for row in pred['annual']:
    y=row['year']
    if y>2018:break
    actual=int(any(regular(a,z) for z in range(origin,y+1)))
    values[fam(a)].append((row['regular_role_reached_by_year'],actual))
 result={}
 for f,rows in values.items():
  x=np.array([r[0] for r in rows]);y=np.array([r[1] for r in rows]);opt=minimize_scalar(lambda power:float(np.mean((x**power-y)**2)),bounds=(.25,4),method='bounded');result[f]={'power':float(opt.x),'rows':len(rows),'outcome_end':2018}
 return result

def apply_regular_calibration(pred,f,calibration):
 power=calibration[f]['power'];prev=0.;masses=[]
 for row in pred['annual']:
  p=min(row['mlb_arrived_by_year'],row['regular_role_reached_by_year']**power);masses.append(max(0,p-prev));row['regular_role_reached_by_year']=p;prev=p
 pred['first_regular_mass']=masses;pred['regular_not_reached_by_horizon_probability']=1-prev
 return pred

def evaluate(selection):
 cases=[];conditional=[]
 for origin in [2019,2020]:
  fit=train_arrival(origin-1,selection['C'],selection['ranked']);pool=donors(origin-1)
  for a in CO:
   if a['year']!=origin or not eligible(a):continue
   pred=apply_regular_calibration(forecast(a,fit,pool,selection['neighbors']),fam(a),selection['regular_calibration']);base=forecast(a,fit,pool,selection['neighbors'],baseline=True);ev=first(a)
   for t,row in enumerate(pred['annual']):
    y=row['year']
    if y>END:break
    reg=any(regular(a,z) for z in range(a['year'],y+1) if z!=2020);ref=509 if fam(a)=='H' else 171;pm=row['mlb_arrived_by_year'];bm=base['annual'][t]['mlb_arrived_by_year']
    cases.append({'id':a['mlbamId'],'name':a['name'],'origin':origin,'year':y,'family':fam(a),'horizon':t+1,'arrival_actual':int(ev is not None and ev<=y),'arrival_pred':pm,'arrival_baseline':bm,'actual_workload':exposure(a['mlbamId'],y,fam(a)),'predicted_workload':row['expected_workload'],'regular_actual':int(reg),'regular_pred':row['regular_role_reached_by_year'],'regular_immediate_benchmark':pm,'regular_one_year_benchmark':pred['annual'][t-1]['mlb_arrived_by_year'] if t else 0,'source_ETA':a.get('ETA')})
   if ev is not None and ev<=END and ev!=2020:
    cp=workload(a,ev-origin,pool,selection['neighbors'],selection['ranked']);actual=exposure(a['mlbamId'],ev,fam(a));role='H' if fam(a)=='H' else 'SP' if AN.get((a['mlbamId'],ev,'P'),{}).get('GS',0)>=5 else 'RP';ref={'H':509,'SP':171,'RP':56.6666666667}[role]
    conditional.append({'id':a['mlbamId'],'name':a['name'],'origin':origin,'debut_year':ev,'role':role,'actual':actual,'predicted':cp['mean'][0],'half_season':ref/2,'full_season':ref,'first_year_regular':int(regular(a,ev))})
 groups={}
 for f in ['H','P','all']:
  rows=[r for r in cases if f=='all' or r['family']==f];ordinary=[r for r in rows if r['year']!=2020]
  groups[f]={'rows':len(rows),'players':len({r['id'] for r in rows}),'arrival_Brier':float(np.mean([(r['arrival_pred']-r['arrival_actual'])**2 for r in rows])),'arrival_baseline_Brier':float(np.mean([(r['arrival_baseline']-r['arrival_actual'])**2 for r in rows])),'regular_Brier':float(np.mean([(r['regular_pred']-r['regular_actual'])**2 for r in ordinary])),'immediate_regular_Brier':float(np.mean([(r['regular_immediate_benchmark']-r['regular_actual'])**2 for r in ordinary])),'one_year_regular_Brier':float(np.mean([(r['regular_one_year_benchmark']-r['regular_actual'])**2 for r in ordinary])),'workload_MAE':float(np.mean([abs(r['actual_workload']-r['predicted_workload']) for r in ordinary])),'workload_bias':float(np.mean([r['predicted_workload']-r['actual_workload'] for r in ordinary]))}
 for f in ['H','SP','RP']:
  rows=[r for r in conditional if r['role']==f]
  if rows:groups['debut_'+f]={'n':len(rows),'mean_actual':float(np.mean([r['actual'] for r in rows])),'median_actual':float(np.median([r['actual'] for r in rows])),'model_MAE':float(np.mean([abs(r['actual']-r['predicted']) for r in rows])),'half_season_MAE':float(np.mean([abs(r['actual']-r['half_season']) for r in rows])),'full_season_MAE':float(np.mean([abs(r['actual']-r['full_season']) for r in rows])),'regular_in_debut_year_fraction':float(np.mean([r['first_year_regular'] for r in rows]))}
 return cases,conditional,groups

def write_csv(path,rows):
 with path.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build():
 selection=select();selection['regular_calibration']=calibrate_regular(selection);rankfree=select(False);rankfree['regular_calibration']=calibrate_regular(rankfree);selection['rank_free']=rankfree;(OUT/'Selection.json').write_text(json.dumps(selection,indent=2)+'\n');print('Selected',selection['C'],selection['neighbors'],flush=True)
 cases,conditional,metrics=evaluate(selection);rf_cases,rf_conditional,rf_metrics=evaluate(rankfree);write_csv(OUT/'Rank_Free_Chronological_Cases.csv',rf_cases);(OUT/'Rank_Free_Validation.json').write_text(json.dumps(rf_metrics,indent=2)+'\n');write_csv(OUT/'Chronological_Cases.csv',cases);write_csv(OUT/'Debut_Workload_Cases.csv',conditional);(OUT/'Validation.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2),flush=True)
 # Current models use all available completed 2025 history; 2026 is not a training outcome.
 fit=train_arrival(END,selection['C']);agnostic=train_arrival(END,rankfree['C'],ranked=False);pool=donors(END)
 html=(ROOT/'trade-analyzer-beta/index.html').read_text();cat=json.loads(gzip.decompress(base64.b64decode(re.search(r"const packed='([^']+)'",html)[1])));eta=json.loads((ROOT/'data/research/eta-evidence.json').read_text());october={a['fantraxId']:a for a in json.loads((ROOT/'data/editions/october-2026.json').read_text())['rankings']};players={}
 for asset in cat['assets']:
  if asset['audit']['kind']!='prospect':continue
  ev=asset.get('prospect_evidence',{});snapshot=ev.get('snapshot',{});globalrank=next((e.get('rank') for e in asset.get('market',{}).get('evidence',[]) if 'Global preseason' in e.get('scope','') and e.get('source')=='FanGraphs'),None);f='P' if asset['audit']['role']!='H' else 'H';ranked=globalrank is not None and globalrank<=fit['support'][f]['max_source_rank']
  profile=october.get(asset['id'],{});birth=profile.get('birthDate');age_now=(datetime.date(2027,4,1)-datetime.date.fromisoformat(birth)).days/365.25 if birth else float(ev.get('saved_age') or 22)+.5;groups=profile.get('seasonStats',{}).get('groups',[]);splits=profile.get('seasonStats',{}).get('splits',[]);starts=sum(float(z.get('starts',0)) for z in groups if z.get('group')=='pitching');games=sum(float(z.get('games',z.get('gamesPlayed',0)) or 0) for z in splits);startfrac=starts/games if games else None;a={'year':2027,'name':asset['name'],'position':asset['position'],'pitcher':int(f=='P'),'age':age_now,'level':profile.get('level') or snapshot.get('level'),'rank':globalrank or 50,'prior_milb_start_fraction':startfrac};sel=selection if ranked else rankfree;pred=apply_regular_calibration(forecast(a,fit if ranked else agnostic,pool,sel['neighbors']),f,sel['regular_calibration']);flags=['Research timing candidate; no central competitive-fit value restored.','Probabilities concern MLB arrival and a workload milestone, not a medical diagnosis or fantasy success.','No future opportunity depth chart or individualized injury data.','Conditional workload is not multiplied into old unconditional prospect value paths.']
  if not ranked:flags.append('No validated global FanGraphs rank input; rank-free age/level model used. Pipeline/DD ranks are not silently converted.')
  if a['level'] not in LEVEL:flags.append('Current level unresolved; explicit missing-level feature used.')
  if min(pred['conditional_support'])<20:flags.append('Longer-horizon workload support below 20 players; tail estimates fragile.')
  players[asset['id']]={'name':asset['name'],'role':asset['audit']['role'],'workload_unit':'PA' if f=='H' else 'IP','inputs':a,'published_eta':eta.get(asset['id']),'rank_input_source':'Dated global FanGraphs preseason rank' if ranked else 'Rank excluded','flags':flags,**pred}
 payload={'version':'Arrival/workload research candidate 2026-10-13','trained_through':2025,'forecast_origin':2027,'status':'Diagnostic candidate; release gates assessed in report','targets':json.loads((OUT/'Protocol.json').read_text())['targets'],'selection':selection,'validation':metrics,'training_support':fit['support'],'rank_free_validation':rf_metrics,'players':players};(ROOT/'data/arrival-workload-model.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
 # Transparent parameter archive; no unsafe pickle needed for reproduction.
 params={}
 for label,m in [('ranked',fit),('rank_free',agnostic)]:
  params[label]={}
  for f,pipe in m['models'].items():
   scale,lr=pipe.steps[0][1],pipe.steps[1][1];params[label][f]={'feature_mean':scale.mean_.tolist(),'feature_scale':scale.scale_.tolist(),'coefficients':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0]),'support':m['support'][f]}
 (OUT/'Parameters.json').write_text(json.dumps(params,indent=2)+'\n')
if __name__=='__main__':build()

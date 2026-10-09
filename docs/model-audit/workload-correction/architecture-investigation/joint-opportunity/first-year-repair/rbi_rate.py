"""Verified individual RBI conversion expert and explicit context availability."""
from engine import *

def rate_features(z):
 rows=z.get('history_override',hist.get((z['id'],'H'),[]));year=z['year'];pastrows=[a for a in rows if year-3<=a['year']<=year and a['stat'].get('PA',0)>0];mass=sum(a['year']-(year-4) for a in pastrows);prior=past.prior_at('H',year);vals={};ex=sum(a['stat']['PA']*(a['year']-(year-4))/mass for a in pastrows) if mass else 0
 for k in ['RBI','HR','TB','BB','R','H']:
  weighted=sum(a['stat'].get(k,0)*(a['year']-(year-4))/mass for a in pastrows) if mass else 0;vals[k]=(weighted+100*prior.get(k,0))/(ex+100)
 return np.array([vals[k] for k in ['RBI','HR','TB','BB','R','H']]+[ex,z['x'][13],z['x'][14],z['x'][13]*vals['RBI']])

def fit_rate(year):
 rows=[a for a in training(year,calendar=True,family='H') if not a['calibration'] and a['actual'].get('PA',0)>=50];X=np.stack([rate_features(a['z']) for a in rows]);y=np.array([a['actual'].get('RBI',0)/a['actual']['PA'] for a in rows]);w=np.array([min(600,a['actual']['PA'])*a['weight'] for a in rows]);reg=make_pipeline(StandardScaler(),Ridge(alpha=500));reg.fit(X,y,ridge__sample_weight=w)
 return reg,{'asof':year,'latest_target':max(a['year'] for a in rows),'rows':len(rows),'fit_ID_mods':[1,2,3],'alpha':500,'target':'RBI per actualPA; fitPA weighting, calendar confidence','no_lineup_context_used':True}

def run():
 dev=[];man=[]
 for year in [2016,2017,2018,2021,2022]:
  reg,mn=fit_rate(year);man.append(mn);xs=[z for z in records['H'] if z['year']==year and z['id']%5==4 and z['positive_anchor']];model=joblib.load(HERE/f'dev-H-{year}.joblib');inc=incumbent(year,'H',xs);pred=opportunity(model,xs,inc,read(HERE/'Selection_Freeze.json')['selected']['H']);rates=np.clip(reg.predict(np.stack([rate_features(z) for z in xs])),0,.3)
  for z,c,rr in zip(xs,pred,rates):
   b=historical_baseline(z)
   if not b:continue
   actual=(target(z) or {}).get('stat',{});current=lookup.get((z['id'],year,'H'),{}).get('stat',{});dev.append({'mlbam_id':z['id'],'anchor':year,'actual':actual.get('RBI',0),'high':current.get('PA',0)>=500 and current.get('RBI',0)>=90,'existing':b['RBI']/b['PA']*c['PA'] if b['PA'] else 0,'individual_rate':float(rr)*c['PA']})
 scores={group:{key:metric([(a[key],a['actual']) for a in dev if group=='all' or a['high']]) for key in ['existing','individual_rate']} for group in ['all','high']};a,b=scores['all']['existing'],scores['all']['individual_rate'];ha,hb=scores['high']['existing'],scores['high']['individual_rate'];accepted=b['MAE']<=a['MAE']-.2 and hb['MAE']<=ha['MAE']+.5 and abs(hb['bias'])<=abs(ha['bias'])+1;selected='individual_rate' if accepted else 'existing'
 put('RBI_Rate_Selection.json',{'selected':selected,'development':scores,'manifest':man,'rule':'>=.2RBI aggregate gain; highproducer MAE <=+.5RBI and absolute bias <=+1RBI; no test selection','context_availability':{'batting_order':'Not stored in frozen annual schema','team_offense':'Current team metadata only; no verified chronological team-year environments','baserunner_opportunities':'Not stored','lineup_continuity':'Not stored','individual_conversion':'Verified annualRBI/PA and HR/TB/BB/R/H, used','established_regression':'100PA feature shrinkage and500ridge penalty; age and tenure used'},'counts_at_fixed_development_workload':True});put('RBI_Rate_Development.json.gz',dev)
 reg,mn=fit_rate(2026);checkpoint(reg,HERE/'current-RBI-rate.joblib',compress=3)
 cases=read(HERE/'H_Cases.json.gz');rows=[]
 for year in sorted({a['anchor'] for a in cases}):
  reg,manifest=fit_rate(year);checkpoint(reg,HERE/f'RBI-rate-{year}.joblib',compress=3);xs=[a for a in cases if a['anchor']==year];zs=[next(z for z in records['H'] if z['id']==a['mlbam_id'] and z['year']==year) for a in xs];rates=np.clip(reg.predict(np.stack([rate_features(z) for z in zs])),0,.3)
  for a,rr in zip(xs,rates):
   rows.append({'mlbam_id':a['mlbam_id'],'name':a['name'],'anchor':year,'shock':year+1==2020,'high':(lookup.get((a['mlbam_id'],year,'H'),{}).get('stat',{}).get('PA',0)>=500 and lookup.get((a['mlbam_id'],year,'H'),{}).get('stat',{}).get('RBI',0)>=90),'actual':a['actual'].get('RBI',0),'baseline':a['baseline']['RBI'],'joint':a['past_only']['RBI'],'workload_repair':a['revised']['RBI'],'individual_rate':float(rr)*a['revised']['PA']})
 test={group:{key:metric([(a[key],a['actual']) for a in rows if not a['shock'] and (group=='all' or a['high'])]) for key in ['baseline','joint','workload_repair','individual_rate']} for group in ['all','high']};put('RBI_Rate_Validation.json',{'selected':selected,'scores':test,'no_test_reselection':True,'not_applied_to_main_forecast':selected=='existing','reason':'General rate estimator development decision; no Soto-specific target.'});put('RBI_Rate_Cases.json.gz',rows);print('RBI',selected,json.dumps(scores),json.dumps(test),flush=True)
if __name__=='__main__':run()

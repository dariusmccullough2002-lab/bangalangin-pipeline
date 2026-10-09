"""Frozen workload correction and chronological comparison; no production writes."""
import sys,json,csv,gzip,hashlib,copy,collections,math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(sys.argv[1]).resolve();CAT=Path(sys.argv[2]).resolve();OUT=Path(__file__).resolve().parent;RAW=OUT/'source-cache'
sys.path.insert(0,str(ROOT/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
v,r,old=m.v,m.r,m.old
assets=json.loads(CAT.read_text())['assets'];by={a['id']:a for a in assets}
# Complete, exhaustive level-season response. Each listing contains one aggregate per player,
# with a last-team label even for numTeams>1. Never sum a player's aggregate and team splits.
index={};manifest=[];duplicates=[]
for y in range(2015,2027):
 for sport in range(11,17):
  name=f'{y}-{sport}';b=gzip.decompress((RAW/(name+'.json.gz')).read_bytes());meta=json.loads((RAW/(name+'.meta.json')).read_text());assert hashlib.sha256(b).hexdigest()==meta['sha256_uncompressed']
  g=json.loads(b)['stats'][0];assert len(g['splits'])==g['totalSplits'];manifest.append(meta|{'season':y,'sport_id':sport})
  seen={}
  for z in g['splits']:
   ident=z['player']['id'];s=z['stat'];notation=str(s['inningsPitched']);whole,frac=(notation.split('.')+['0'])[:2];assert frac in ['0','1','2'];outs=3*int(whole)+int(frac);assert s.get('outs',outs)==outs
   # Same player/level/season records must agree; an ambiguity blocks scoring.
   if ident in seen:
    assert seen[ident]['outs']==outs,('ambiguous aggregate',name,ident);duplicates.append((name,ident));continue
   record={'mlbam_id':ident,'season':y,'sport_id':sport,'outs':outs,'IP':outs/3,'numTeams':z.get('numTeams',1),'team_label':z.get('team',{}),'source_url':meta['url'],'retrieved_utc':meta['retrieved_utc'],'source_sha256':meta['sha256_uncompressed']};seen[ident]=record
  for ident,z in seen.items():index.setdefault((ident,y),[]).append(z)
def minor(ident,y):
 assert 2015<=y<=2026
 return sum(z['outs'] for z in index.get((ident,y),[]))/3

def estimate(rows,rr,year,ident,combined=False):
 rows=[z for z in rows if year-3<=z['year']<=year and z['role']==rr and r.exposure(z['stat'],rr)>0]
 if not rows or not any(z['year']>=year-2 for z in rows):return None
 weights={year-3:.1,year-2:.2,year-1:.3,year:.4};mass=sum(weights[z['year']] for z in rows)
 mlb=[r.exposure(z['stat'],rr) for z in rows];workloads=[ip+(minor(ident,z['year']) if combined and r.age_at(ident,z['year'])<=26 else 0) for z,ip in zip(rows,mlb)]
 recent=sum(ip*weights[z['year']]/mass for z,ip in zip(rows,workloads));healthy=float(np.median(sorted(workloads,reverse=True)[:2]));pw=1/(len(rows)+3)
 prior=float(np.median([r.exposure(z['stat'],rr) for z in old.cal if z['role']==rr]));work=min(v.cf.cap(rr),(1-pw)*(.7*recent+.3*healthy)+pw*prior)
 mlbrecent=sum(ip*weights[z['year']]/mass for z,ip in zip(rows,mlb));rates={k:(sum(z['stat'].get(k,0)*weights[z['year']]/mass for z in rows)+30*old.prior[rr][k])/(mlbrecent+30) for k in old.fields[rr]}
 return rates,work

def project(f,rr,age):
 rates,work=f;q=int(np.searchsorted(v.base.CUTS[rr],r.surplus({k:x*work for k,x in rates.items()},rr)/work*r.REFERENCE[rr]));c=v.curve(rr,age,q);z=c['path'][0];s={k:x*z['rates'].get(k,1)*work*z['workload'] for k,x in rates.items()};s['QA3']=min(s['QA3'],s['IP']/5);return s
# All335 currently inventoried seasons, including role changes.
coverage=list(csv.DictReader((OUT.parent/'Young_Pitcher_Season_Coverage.csv').open()));evidence=[]
for z in coverage:
 a=by[z['id']];ident=v.cf.IDS.get(a['id'],old.players[a['id']].get('mlbamId'));year=int(z['season']);components=index.get((ident,year),[]);ip=minor(ident,year)
 z.update(mlbam_id=ident,verified_MiLB_IP=ip,combined_IP=float(z['MLB_IP'])+ip,status='Verified official six-level affiliated workload',source=';'.join(t['source_url'] for t in components) or 'Exhaustive six-level queries: no recorded affiliated MiLB IP')
 evidence.append({'id':z['id'],'mlbam_id':ident,'season':year,'MiLB_IP':ip,'components':components,'coverage':'All six affiliated sports queried; no absent-record zero inferred from failed requests'})
with (OUT/'Completed_Young_Pitcher_Season_Coverage.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
# Current before/after with every affected identity. Preserve original m.paths talent/curves.
original=v.recent_forecast;current=[];maxparity=0
for ident in sorted({z['id'] for z in coverage}):
 a=by[ident];p=old.players[ident];au=a['audit'].get('MLB',a['audit']);rr=au.get('role');mlbam=v.cf.IDS.get(a['id'],p.get('mlbamId'));hist=v.seasons(p,rr)
 if rr not in ['SP','RP']:continue
 f=estimate(hist,rr,2026,mlbam);g=estimate(hist,rr,2026,mlbam,True);assert f[0]==g[0]
 maxparity=max(maxparity,abs(f[1]-original(p,rr)[1]));assert abs(f[1]-original(p,rr)[1])<1e-8
 def experimental(q,role,scenario='base'):
  out=original(q,role,scenario)
  if q['id']==ident and role==rr and out:
   aa=copy.deepcopy(out[2]);aa['projected_workload']=g[1];return out[0],g[1],aa
  return out
 v.recent_forecast=experimental
 try:
  paths,aa=m.paths(p);aa=aa.get('MLB',aa);assert aa['projection_audit']['talent_rates']==au['projection_audit']['talent_rates'];new=aa['projection'];neutral=m.competitive(paths,'neutral')['display']
 finally:v.recent_forecast=original
 current.append({'id':ident,'name':a['name'],'owner':a['owner'],'role':rr,'age':p['age'],'baseline':au['projection'],'experimental':new,'baseline_neutral':a['values']['neutral']['display'],'experimental_neutral':neutral,'neutral_delta':neutral-a['values']['neutral']['display'],'baseline_preaging_IP':f[1],'combined_preaging_IP':g[1],'talent_rates_identical':True,'frozen_cap':v.cf.cap(rr)})
# Historical identities held out from direct aging-curve construction; no refit.
history={};future={}
for z in old.AN:
 if z['role']=='H':continue
 q=copy.deepcopy(z);q['role']=v.observed_role(v.appearance_history().get((q['id'],q['year']),{}),q['role']);history.setdefault(q['id'],[]).append(q);future[(q['id'],q['year'])]=q
cases=[]
for ident,hist in history.items():
 if ident%5!=0:continue
 for anchor in [2018,2022]:
  z=next((z for z in hist if z['year']==anchor and z['stat'].get('IP',0)>0),None)
  if not z:continue
  age=r.age_at(ident,anchor)
  if age is None or not math.isfinite(age) or age>26:continue
  rr=z['role'];f=estimate(hist,rr,anchor,ident);g=estimate(hist,rr,anchor,ident,True)
  if not f or not g:continue
  assert f[0]==g[0];b=project(f,rr,int(round(age)));c=project(g,rr,int(round(age)));actual=future.get((ident,anchor+1));target=actual['stat'] if actual else {}
  info=v.appearance_history().get((ident,anchor),{});gp=info.get('GP',0);gs=info.get('GS',0);frac=gs/gp if gp else None
  prior=[x['stat'].get('IP',0)+minor(ident,x['year']) for x in hist if anchor-3<=x['year']<anchor]
  total=z['stat']['IP']+minor(ident,anchor);shortfall=bool(prior and total<.6*max(prior))
  sub=['all',rr,'promoted' if minor(ident,anchor)>0 else 'MLB_only_anchor']
  if frac is not None and 0<frac<1:sub.append('swingmen')
  if shortfall:sub.append('workload_shortfall_proxy_not_diagnosed_injury')
  cases.append({'mlbam_id':ident,'name':z['name'],'anchor':anchor,'target_year':anchor+1,'age':age,'role':rr,'subgroups':sub,'baseline':b,'experimental':c,'actual':target,'anchor_minor_IP':minor(ident,anchor),'future_role':actual['role'] if actual else 'absent','rate_parity':True})
scores={}
for group in sorted({g for z in cases for g in z['subgroups']}):
 xs=[z for z in cases if group in z['subgroups']];metrics={}
 for k in ['IP','K','QA3']:
  metrics[k]={}
  for method in ['baseline','experimental']:
   errors=[z[method].get(k,0)-z['actual'].get(k,0) for z in xs];metrics[k][method]={'MAE':float(np.mean(np.abs(errors))),'bias':float(np.mean(errors)),'RMSE':float(np.sqrt(np.mean(np.array(errors)**2)))}
 scores[group]={'n':len(xs),'unique_players':len(set(z['mlbam_id'] for z in xs)),'metrics':metrics}
byyear={}
for year in [2018,2022]:
 xs=[z for z in cases if z['anchor']==year];byyear[str(year)]={'n':len(xs),'IP_MAE':{method:float(np.mean([abs(z[method]['IP']-z['actual'].get('IP',0)) for z in xs])) for method in ['baseline','experimental']}}
# Workload invariance within the existing season window. Across the first MLB boundary,
# eligibility/role routing still changes: adding MiLB IP alone cannot remove that jump.
boundary={'same_season_reallocation':'For a fixed positive MLB season and fixed talent rates, total workload is invariant to moving innings from MiLB to MLB.','first_MLB_boundary':'UNRESOLVED: MiLB-only seasons remain excluded; introducing the first positive MLB season changes forecast existence, prior weight and role routing.','tiny_MLB_caution':'A season with tiny MLB IP plus substantial MiLB IP can unlock near-full professional workload at that season’s MLB primary role. This needs a reliability/role boundary policy before release, not an automatic value boost.'}
allscore=scores['all']['metrics'];worsening=[k for k in ['IP','K','QA3'] if allscore[k]['experimental']['MAE']>allscore[k]['baseline']['MAE']]
result={'status':'EXPERIMENTAL; NO PRODUCTION CHANGES','catalog_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'coverage':{'seasons':len(coverage),'verified':len(coverage),'positive_MiLB':sum(float(z['verified_MiLB_IP'])>0 for z in coverage),'zero_recorded_affiliated_MiLB':sum(float(z['verified_MiLB_IP'])==0 for z in coverage),'source_requests':len(manifest),'deduplicated_identical_records':len(duplicates)},'current_pitchers':len(current),'current_workload_changed':sum(abs(z['combined_preaging_IP']-z['baseline_preaging_IP'])>1e-8 for z in current),'max_baseline_workload_reproduction_error':maxparity,'scores':scores,'chronological_results':byyear,'promotion_boundary':boundary,'release_recommendation':'DO NOT RELEASE: promotion boundary unresolved; '+('aggregate MAE worsens for '+','.join(worsening) if worsening else 'subgroup/bias/injury and boundary gates require review'),'limitations':['Frozen priors/caps/aging curves inherited; historical audit is a paired out-of-sample identity/year comparison, not a newly fit fully chronological engine.','Two anchor cohorts; modest subgroup samples, not universal injury safety certification.','Workload-shortfall proxy is not an independently verified injury diagnosis.','Affiliated MiLB physical workload includes rehab innings; these do not establish starter readiness.','Foreign, independent, college and winter-league workload excluded.']}
for name,obj in [('Workload_Validation.json',result),('Current_Before_After.json',current),('Historical_Cases.json',cases),('Verified_Season_Evidence.json',evidence),('Source_Manifest.json',manifest)]:
 (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False))
print(json.dumps(result,indent=2))

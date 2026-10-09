"""Read-only audit; no calibration or catalog writes. Run with recovery root + catalog + output directory."""
import sys,json,copy,math,hashlib,csv
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(sys.argv[1]).resolve();CAT=Path(sys.argv[2]).resolve();OUT=Path(sys.argv[3]).resolve();OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
v=m.v;r=m.r;old=m.old
D=json.loads(CAT.read_text());by={a['name']:a for a in D['assets']}
names=['Jacob Misiorowski','Cade Smith','Paul Skenes','Tarik Skubal','Zack Wheeler','Garrett Crochet','Josh Hader','Edwin Diaz','Tyler Holton','Reid Detmers','Mason Montgomery','Andrew Morris','Fernando Tatis Jr.','Roman Anthony','Aaron Judge','Juan Soto','Bobby Witt Jr.','Jackson Chourio','Jackson Holliday','Henry Bolte','Corey Seager','Ronald Acuna Jr.']
def role_row(z):
 if z['role']=='H':return 'H'
 return v.observed_role(v.appearance_history().get((z['id'],z['year']),{}),z['role'])
def estimate(rows,rr,year,latest=False):
 rows=[z for z in rows if year-3<=z['year']<=year and z['role']==rr and r.exposure(z['stat'],rr)>0]
 if not rows or not any(z['year']>=year-2 for z in rows):return None
 if latest:rows=[max(rows,key=lambda z:z['year'])]
 weights={year-3:.1,year-2:.2,year-1:.3,year:.4};mass=sum(weights[z['year']] for z in rows)
 recent=sum(z['stat'].get('PA' if rr=='H' else 'IP',0)*weights[z['year']]/mass for z in rows)
 healthy=float(np.median(sorted([r.exposure(z['stat'],rr) for z in rows],reverse=True)[:2]));pw=1/(len(rows)+3)
 work=min(v.cf.cap(rr),(1-pw)*(.7*recent+.3*healthy)+pw*r.REFERENCE[rr]);strength=100 if rr=='H' else 30
 rates={k:(sum(z['stat'].get(k,0)*weights[z['year']]/mass for z in rows)+strength*old.prior[rr][k])/(recent+strength) for k in old.fields[rr]}
 return rates,work
def project(rates,work,rr,age):
 q=int(np.searchsorted(v.base.CUTS[rr],r.surplus({k:x*work for k,x in rates.items()},rr)/work*r.REFERENCE[rr]));c=v.curve(rr,age,q);z=c['path'][0]
 s={k:x*z['rates'].get(k,1)*work*z['workload'] for k,x in rates.items()}
 if rr=='H':s=v.reconcile(s)
 else:s['QA3']=min(s['QA3'],s['IP']/5)
 return s,c
rows=[];checks=[]
for name in names:
 if name not in by:continue
 a=by[name];p=old.players[a['id']];au=a['audit'].get('MLB',a['audit']);rr=au.get('role');base=au.get('projection')
 if rr not in ['H','SP','RP'] or not base:continue
 ps,audit=m.paths(p);aa=audit.get('MLB',audit);err=max(abs(aa['projection'][k]-x) for k,x in base.items());assert err<1e-8,(name,err)
 neutral=m.competitive(ps,'neutral')['display'];assert abs(neutral-a['values']['neutral']['display'])<1e-8
 hist=v.seasons(p,rr);f=estimate(hist,rr,2026,True);alt,c=project(*f,rr,int(round(p.get('age') or 26)))
 d=au['projection_audit'];rate=d['talent_rates'];cur=max([z for z in hist if z['role']==rr and r.exposure(z['stat'],rr)>0],key=lambda z:z['year'])
 rows.append({'name':name,'id':a['id'],'role':rr,'age':p.get('age'),'neutral_unchanged':neutral,'current':cur,'baseline':base,'latest_season_only_sensitivity':alt,'pre_aging_workload':d['projected_workload'],'pre_aging_rates':rate,'first_year_workload_multiplier':base.get('PA',base.get('IP'))/d['projected_workload'],'rate_pseudocount_actual':100 if rr=='H' else 30,'diagnostic_pseudocount_displayed':d.get('rate_prior_strength'),'latest_sensitivity_support':{k:c[k] for k in ['anchors','unique_players','age_band','starting_contribution_quartile']},'individual_prospect_prior_present':bool(p.get('prospect') or a.get('prospect_evidence'))})
 checks.append({'name':name,'projection_max_error':err,'neutral_error':neutral-a['values']['neutral']['display']})
# Previously inspected identity-held-out 2017 anchors only; no reserved2021 cohort.
# Protocol fixed before scoring: latest-season-only ablation; same priors, caps, cohorts,
# reconciliation and utility. No model selection from these results.
history={};future={}
for z in old.AN:
 q=copy.deepcopy(z);q['role']=role_row(q);history.setdefault(q['id'],[]).append(q);future[(q['id'],q['year'],q['role'])]=q
cases=[]
for rr in ['H','SP','RP']:
 for a in v.base.ALL_COHORTS[rr]:
  if a['year']!=2017 or a['id']%5!=0:continue
  hist=history[a['id']];f=estimate(hist,rr,2017);g=estimate(hist,rr,2017,True)
  if not f or not g:continue
  actual=future.get((a['id'],2018,rr));target=actual['stat'] if actual else {}
  age=int(round(r.age_at(a['id'],2017)));b,_=project(*f,rr,age);c,_=project(*g,rr,age)
  cases.append({'id':a['id'],'name':a.get('name') or next(z['name'] for z in hist),'role':rr,'actual':target,'baseline':b,'latest':c})
scores={}
for rr in ['H','SP','RP']:
 xs=[z for z in cases if z['role']==rr];fields=['PA','HR','SB','H','TB'] if rr=='H' else ['IP','K','ER','QA3','SV','HLD']
 scores[rr]={'n':len(xs),'metrics':{k:{method:{'MAE':float(np.mean([abs(z[method].get(k,0)-z['actual'].get(k,0)) for z in xs])),'bias':float(np.mean([z[method].get(k,0)-z['actual'].get(k,0) for z in xs]))} for method in ['baseline','latest']} for k in fields}}
# Conditional workload illustration: external2026 ZiPS PA is a reference, not a2027 target.
p=old.players[by['Roman Anthony']['id']];original=v.recent_forecast;_,aa=m.paths(p);factor=588/aa['projection']['PA']
def diagnostic(q,rr,scenario='base'):
 out=original(q,rr,scenario)
 if q['id']==p['id'] and rr=='H' and out:
  audit=copy.deepcopy(out[2]);audit['projected_workload']=out[1]*factor
  return out[0],out[1]*factor,audit
 return out
v.recent_forecast=diagnostic
try:
 ps,aa=m.paths(p);illustration={'label':'Conditional588PA workload illustration only; not a validated correction','projection':aa['projection'],'neutral':m.competitive(ps,'neutral')['display'],'pre_aging_workload':aa['projection_audit']['projected_workload'],'original_neutral':by['Roman Anthony']['values']['neutral']['display']}
 (OUT/'Roman_Workload_Illustration.json').write_text(json.dumps(illustration,indent=2))
finally:v.recent_forecast=original
# Verified workload-only substitution:2025 AAA63⅓ + MLB66; talent still MLB-only.
p=old.players[by['Jacob Misiorowski']['id']];original=v.recent_forecast
hist=[z for z in v.seasons(p,'SP') if 2023<=z['year']<=2026 and z['role']=='SP' and z['stat']['IP']>0]
workloads={z['year']:z['stat']['IP']+(63+1/3 if z['year']==2025 else 0) for z in hist};weights={2023:.1,2024:.2,2025:.3,2026:.4};mass=sum(weights[y] for y in workloads)
recent=sum(workloads[y]*weights[y]/mass for y in workloads);healthy=float(np.median(sorted(workloads.values(),reverse=True)[:2]));pw=1/(len(workloads)+3);work=min(v.cf.cap('SP'),(1-pw)*(.7*recent+.3*healthy)+pw*r.REFERENCE['SP'])
def diagnostic(q,rr,scenario='base'):
 out=original(q,rr,scenario)
 if q['id']==p['id'] and rr=='SP' and out:
  audit=copy.deepcopy(out[2]);audit['projected_workload']=work
  return out[0],work,audit
 return out
v.recent_forecast=diagnostic
try:
 ps,aa=m.paths(p);illustration={'label':'Workload-only combined professional innings; verified2025AAA input; not validated for release','2025_MLB_IP':66,'2025_AAA_IP':63+1/3,'2025_combined_IP':129+1/3,'projection':aa['projection'],'neutral':m.competitive(ps,'neutral')['display'],'pre_aging_workload':work,'talent_rates_unchanged':aa['projection_audit']['talent_rates']==by['Jacob Misiorowski']['audit']['projection_audit']['talent_rates'],'source':'https://baseballsavant.mlb.com/savant-player/jacob-misiorowski-694819'}
 (OUT/'Misiorowski_Combined_Workload.json').write_text(json.dumps(illustration,indent=2))
finally:v.recent_forecast=original
qa={'formula':'(outs >= 15 and ER <= 2) OR (outs >= 18 and ER <= 3)','forecast_method':'Historical QA3 per IP, role prior regression and age/cohort rate multiplier; capped at IP/5. No explicit projected-start count or start-depth model. Relief QA3 may be nonzero if a long relief appearance qualifies.','raw_game_replay':'Compact annual/weekly Retrosheet input retained; individual raw appearance files absent, so exact raw event replay not certified.'}
result={'baseline_catalog_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'status':'DIAGNOSTIC ONLY; no numerical changes adopted','protocol':'Latest-season-only ablation, frozen constants, no parameter tuning; historical2017/2018 identity holdout already inspected; no untouched holdout or full original-input certification','representatives':rows,'parity_checks':checks,'historical_scores':scores,'historical_cases':cases,'QA3':qa}
(OUT/'Projection_Diagnostics.json').write_text(json.dumps(result,indent=2,allow_nan=False))
with (OUT/'Representative_Projections.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['name','role','neutral_UNCHANGED','category','live_baseline','latest_only_DIAGNOSTIC_NOT_CANDIDATE'])
 for z in rows:
  for k,x in z['baseline'].items():w.writerow([z['name'],z['role'],z['neutral_unchanged'],k,x,z['latest_season_only_sensitivity'][k]])
print(json.dumps({'representative_n':len(rows),'historical_scores':scores,'parity':'PASS'},indent=2))
